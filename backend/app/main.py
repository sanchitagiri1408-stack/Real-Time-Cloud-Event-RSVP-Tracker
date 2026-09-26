from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from .config import cors_list
from .database import Base, engine, get_db
from .models import User, Event, RSVP, Announcement, Notification, Waitlist
from .schemas import *
from .auth import hash_password, verify_password, create_token, current_user, require_role
from .services import VALID_RSVPS, counts, create_notification, audit
from .realtime import manager

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Real-Time Cloud Event RSVP Tracker", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=cors_list(), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "event-rsvp-api"}

@app.post("/api/register", response_model=TokenOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(409, "Email is already registered")
    role = data.role.upper()
    if role not in {"ATTENDEE", "ORGANIZER"}:
        role = "ATTENDEE"
    user = User(name=data.name.strip(), email=data.email.lower(), password_hash=hash_password(data.password), role=role)
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_token(user.id), "user": user}

@app.post("/api/login", response_model=TokenOut)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return {"access_token": create_token(user.id), "user": user}

@app.post("/api/logout")
def logout():
    # JWT logout is client-side token disposal; production systems may add token revocation.
    return {"message": "Logged out. Remove the access token on the client."}

@app.get("/api/me", response_model=UserOut)
def me(user=Depends(current_user)):
    return user

@app.post("/api/events", response_model=EventOut, status_code=201)
def create_event(data: EventCreate, user=Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    if data.start_time >= data.end_time:
        raise HTTPException(400, "End time must be after start time")
    event = Event(**data.model_dump(), organizer_id=user.id, status="PUBLISHED")
    db.add(event); db.commit(); db.refresh(event)
    audit(db, user.id, "CREATE_EVENT", "EVENT", event.id); db.commit()
    return event

@app.get("/api/events", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(Event.event_date, Event.start_time).all()

@app.get("/api/events/upcoming", response_model=list[EventOut])
def upcoming(db: Session = Depends(get_db)):
    today = datetime.utcnow().date().isoformat()
    return db.query(Event).filter(Event.event_date >= today, Event.status.in_({"PUBLISHED","FULL"})).order_by(Event.event_date, Event.start_time).all()

@app.get("/api/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    return event

@app.put("/api/events/{event_id}", response_model=EventOut)
def update_event(event_id: int, data: EventCreate, user=Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    if event.organizer_id != user.id: raise HTTPException(403, "You can modify only your own events")
    if data.start_time >= data.end_time: raise HTTPException(400, "End time must be after start time")
    for k, v in data.model_dump().items(): setattr(event, k, v)
    event.updated_at = datetime.utcnow()
    db.commit(); db.refresh(event)
    audit(db, user.id, "UPDATE_EVENT", "EVENT", event.id); db.commit()
    return event

@app.delete("/api/events/{event_id}")
def delete_event(event_id: int, user=Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    if event.organizer_id != user.id: raise HTTPException(403, "You can delete only your own events")
    event.status = "CANCELLED"
    db.commit()
    return {"message": "Event cancelled"}

@app.post("/api/events/{event_id}/rsvp", response_model=RSVPOut)
async def rsvp(event_id: int, data: RSVPRequest, user=Depends(current_user), db: Session = Depends(get_db)):
    status_value = data.status.upper()
    if status_value not in VALID_RSVPS: raise HTTPException(400, "Invalid RSVP status")
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    existing = db.query(RSVP).filter(RSVP.event_id == event_id, RSVP.user_id == user.id).first()

    # SQLite local mode cannot provide row-level locks; PostgreSQL deployments should use
    # a transaction/conditional SQL function for the final-seat guarantee.
    if status_value == "GOING":
        current = db.query(RSVP).filter(RSVP.event_id == event_id, RSVP.status == "GOING", RSVP.user_id != user.id).count()
        if current >= event.maximum_capacity and not (existing and existing.status == "GOING"):
            # Optional waitlist: FIFO position.
            if not db.query(Waitlist).filter(Waitlist.event_id == event_id, Waitlist.user_id == user.id).first():
                pos = db.query(Waitlist).filter(Waitlist.event_id == event_id).count() + 1
                db.add(Waitlist(event_id=event_id, user_id=user.id, position=pos))
                db.commit()
            raise HTTPException(409, "Event is full. You have been added to the waitlist.")
    if existing:
        existing.status = status_value
        existing.updated_at = datetime.utcnow()
        record = existing
    else:
        record = RSVP(event_id=event_id, user_id=user.id, status=status_value)
        db.add(record)
    db.commit(); db.refresh(record)
    c = counts(db, event_id)
    event.status = "FULL" if c["GOING"] >= event.maximum_capacity else "PUBLISHED"
    create_notification(db, user.id, event_id, "RSVP", f"Your RSVP is {status_value}.")
    audit(db, user.id, "RSVP", "EVENT", event_id)
    db.commit()
    await manager.broadcast(event_id, {"type": "RSVP_UPDATED", "event_id": event_id, "counts": c})
    return record

@app.put("/api/events/{event_id}/rsvp", response_model=RSVPOut)
async def update_rsvp(event_id: int, data: RSVPRequest, user=Depends(current_user), db: Session = Depends(get_db)):
    return await rsvp(event_id, data, user, db)

@app.delete("/api/events/{event_id}/rsvp")
async def cancel_rsvp(event_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    record = db.query(RSVP).filter(RSVP.event_id == event_id, RSVP.user_id == user.id).first()
    if not record: raise HTTPException(404, "RSVP not found")
    db.delete(record); db.commit()
    c = counts(db, event_id)
    await manager.broadcast(event_id, {"type": "RSVP_UPDATED", "event_id": event_id, "counts": c})
    return {"message": "RSVP cancelled", "counts": c}

@app.get("/api/events/{event_id}/rsvp", response_model=RSVPOut | None)
def my_rsvp(event_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    return db.query(RSVP).filter(RSVP.event_id == event_id, RSVP.user_id == user.id).first()

@app.get("/api/events/{event_id}/rsvps", response_model=list[RSVPOut])
def event_rsvps(event_id: int, user=Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event: raise HTTPException(404, "Event not found")
    if event.organizer_id != user.id: raise HTTPException(403, "Not your event")
    return db.query(RSVP).filter(RSVP.event_id == event_id).all()

@app.get("/api/events/{event_id}/analytics")
def analytics(event_id: int, user=Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event or event.organizer_id != user.id: raise HTTPException(403, "Access denied")
    c = counts(db, event_id)
    total = c["total"]
    return {**c, "response_rate": round(total / max(total, 1) * 100, 2), "capacity_utilization": round(c["GOING"] / event.maximum_capacity * 100, 2),
            "waitlist_count": db.query(Waitlist).filter(Waitlist.event_id == event_id, Waitlist.status == "WAITLISTED").count()}

@app.post("/api/events/{event_id}/announcements", response_model=AnnouncementOut)
async def announcement(event_id: int, data: AnnouncementCreate, user=Depends(require_role("ORGANIZER")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event or event.organizer_id != user.id: raise HTTPException(403, "Access denied")
    item = Announcement(event_id=event_id, **data.model_dump())
    db.add(item)
    attendees = db.query(RSVP).filter(RSVP.event_id == event_id, RSVP.status.in_({"GOING","MAYBE"})).all()
    for r in attendees:
        create_notification(db, r.user_id, event_id, "ANNOUNCEMENT", data.title + ": " + data.message)
    db.commit(); db.refresh(item)
    await manager.broadcast(event_id, {"type": "ANNOUNCEMENT", "title": data.title, "message": data.message})
    return item

@app.get("/api/events/{event_id}/announcements", response_model=list[AnnouncementOut])
def announcements(event_id: int, db: Session = Depends(get_db)):
    return db.query(Announcement).filter(Announcement.event_id == event_id).order_by(Announcement.created_at.desc()).all()

@app.get("/api/notifications", response_model=list[NotificationOut])
def notifications(user=Depends(current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user.id).order_by(Notification.created_at.desc()).all()

@app.put("/api/notifications/{notification_id}/read")
def mark_read(notification_id: int, user=Depends(current_user), db: Session = Depends(get_db)):
    n = db.get(Notification, notification_id)
    if not n or n.user_id != user.id: raise HTTPException(404, "Notification not found")
    n.read = True; db.commit()
    return {"message": "Notification marked as read"}

@app.websocket("/ws/events/{event_id}")
async def event_socket(websocket: WebSocket, event_id: int):
    await manager.connect(event_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(event_id, websocket)
