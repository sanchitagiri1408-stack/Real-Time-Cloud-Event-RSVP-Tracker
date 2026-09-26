import React, {useEffect, useState} from "react";
import {createRoot} from "react-dom/client";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const token = () => localStorage.getItem("token");
const headers = () => ({ "Content-Type":"application/json", ...(token()?{"Authorization":`Bearer ${token()}`}:{}) });
async function api(path, options={}) {
  const r = await fetch(API+path, {headers:headers(), ...options});
  const data = await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function Auth({onLogin}) {
  const [login,setLogin]=useState(true), [form,setForm]=useState({name:"",email:"",password:"",role:"ATTENDEE"});
  const submit=async e=>{e.preventDefault(); try{
    const data=await api(login?"/api/login":"/api/register",{method:"POST",body:JSON.stringify(login?{email:form.email,password:form.password}:form)});
    localStorage.setItem("token",data.access_token); onLogin(data.user);
  }catch(err){alert(err.message)}};
  return <div className="auth"><div className="card"><h1>Cloud Event RSVP</h1><p>Real-time cloud computing project</p>
    <form onSubmit={submit}>{!login&&<input placeholder="Name" required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/>}
    <input type="email" placeholder="Email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/>
    <input type="password" placeholder="Password" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/>
    {!login&&<select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}><option>ATTENDEE</option><option>ORGANIZER</option></select>}
    <button>{login?"Login":"Register"}</button></form>
    <button className="link" onClick={()=>setLogin(!login)}>{login?"Create account":"Already have an account? Login"}</button>
  </div></div>
}

function EventCard({event,user}) {
  const [counts,setCounts]=useState({GOING:0,MAYBE:0,NOT_GOING:0,available:event.maximum_capacity});
  const [mine,setMine]=useState(null);
  useEffect(()=>{api(`/api/events/${event.id}/analytics`).then(setCounts).catch(()=>{}); api(`/api/events/${event.id}/rsvp`).then(setMine).catch(()=>{});
    const ws=new WebSocket(API.replace(/^http/,"ws")+`/ws/events/${event.id}`);
    ws.onmessage=e=>{const m=JSON.parse(e.data); if(m.type==="RSVP_UPDATED")setCounts(m.counts)};
    return()=>ws.close();
  },[event.id]);
  const rsvp=async status=>{try{const r=await api(`/api/events/${event.id}/rsvp`,{method:"POST",body:JSON.stringify({status})});setMine(r)}catch(e){alert(e.message)}};
  return <div className="card event"><h3>{event.event_name}</h3><p>{event.description}</p>
    <small>{event.event_date} · {event.start_time}-{event.end_time} · {event.venue}</small>
    <div className="stats"><span>Going <b>{counts.GOING||0}</b></span><span>Maybe <b>{counts.MAYBE||0}</b></span><span>Not Going <b>{counts.NOT_GOING||0}</b></span><span>Seats <b>{counts.available??event.maximum_capacity}</b></span></div>
    {user.role==="ATTENDEE"&&<div className="actions">{["GOING","MAYBE","NOT_GOING"].map(s=><button key={s} className={mine?.status===s?"active":""} onClick={()=>rsvp(s)}>{s.replace("_"," ")}</button>)}</div>}
  </div>
}

function Organizer({events,onRefresh}) {
  const [form,setForm]=useState({event_name:"Cloud Computing Workshop",description:"Live cloud architecture demonstration",event_type:"Workshop",event_date:"2099-01-01",start_time:"10:00",end_time:"12:00",venue:"Virtual Lab",maximum_capacity:100,registration_deadline:"2098-12-31"});
  const [selected,setSelected]=useState(null), [analytics,setAnalytics]=useState(null);
  const create=async e=>{e.preventDefault();try{await api("/api/events",{method:"POST",body:JSON.stringify({...form,maximum_capacity:Number(form.maximum_capacity)})});alert("Event created");onRefresh()}catch(x){alert(x.message)}};
  useEffect(()=>{if(selected)api(`/api/events/${selected}/analytics`).then(setAnalytics).catch(()=>{})},[selected]);
  useEffect(() => {
  if (!selected) return;

  const wsUrl =
    API.replace(/^http/, "ws") +
    `/ws/events/${selected}`;

  console.log("Connecting organizer WebSocket:", wsUrl);

  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log("Organizer WebSocket connected");
  };

  ws.onmessage = async (e) => {
    try {
      const message = JSON.parse(e.data);

      console.log("Organizer WebSocket message:", message);

      if (message.type === "RSVP_UPDATED") {
        console.log("RSVP update received. Refreshing analytics...");

        const freshAnalytics =
          await api(`/api/events/${selected}/analytics`);

        setAnalytics(freshAnalytics);
      }

    } catch (error) {
      console.error("WebSocket message error:", error);
    }
  };

  ws.onerror = (error) => {
    console.error("Organizer WebSocket error:", error);
  };

  ws.onclose = () => {
    console.log("Organizer WebSocket disconnected");
  };

  return () => {
    console.log("Closing organizer WebSocket");
    ws.close();
  };

}, [selected]);
  return <div><div className="card"><h2>Organizer Dashboard</h2><form className="grid" onSubmit={create}>{["event_name","description","event_date","start_time","end_time","venue","maximum_capacity","registration_deadline"].map(k=><input key={k} placeholder={k} value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/>)}<button>Create Event</button></form></div>
  {events.map(e=><div className="card" key={e.id}><h3>{e.event_name}</h3><p>Status: <b>{e.status}</b> · Capacity: {e.maximum_capacity}</p><button onClick={()=>setSelected(e.id)}>View Live Analytics</button>{selected===e.id&&analytics&&<div className="stats"><span>Going <b>{analytics.GOING}</b></span><span>Maybe <b>{analytics.MAYBE}</b></span><span>Not Going <b>{analytics.NOT_GOING}</b></span><span>Utilization <b>{analytics.capacity_utilization}%</b></span></div>}</div>)}</div>
}

function App(){
 const [user,setUser]=useState(null),[events,setEvents]=useState([]),[loading,setLoading]=useState(true);
 const load=()=>api("/api/events").then(setEvents).finally(()=>setLoading(false));
 useEffect(()=>{if(token())api("/api/me").then(setUser).catch(()=>localStorage.removeItem("token"));else setLoading(false)},[]);
 useEffect(()=>{if(user)load()},[user]);
 if(loading)return <div className="auth">Loading...</div>;
 if(!user)return <Auth onLogin={setUser}/>;
 return <main><header><div><h1>Real-Time Event Planning</h1><p>Signed in as {user.name} · {user.role}</p></div><button onClick={()=>{localStorage.clear();setUser(null)}}>Logout</button></header>
 {user.role==="ORGANIZER"?<Organizer events={events.filter(e=>e.organizer_id===user.id)} onRefresh={load}/>:<><h2>Discover Events</h2>{events.map(e=><EventCard key={e.id} event={e} user={user}/>)}</>}</main>
}
createRoot(document.getElementById("root")).render(<App/>);
