from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import RSVP, Event, Notification, Announcement, Waitlist, AuditLog

VALID_RSVPS = {"GOING", "MAYBE", "NOT_GOING"}

def counts(db: Session, event_id: int):
    rows = db.query(RSVP.status, func.count(RSVP.id)).filter(RSVP.event_id == event_id).group_by(RSVP.status).all()
    result = {"GOING": 0, "MAYBE": 0, "NOT_GOING": 0}
    for status, count in rows:
        result[status] = count
    result["total"] = sum(result.values())
    event = db.get(Event, event_id)
    result["capacity"] = event.maximum_capacity
    result["available"] = max(event.maximum_capacity - result["GOING"], 0)
    return result

def create_notification(db, user_id, event_id, ntype, message):
    db.add(Notification(user_id=user_id, event_id=event_id, type=ntype, message=message))

def audit(db, user_id, action, entity_type, entity_id=None):
    db.add(AuditLog(user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id))
