# REST API

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| POST | /api/register | Register | Public |
| POST | /api/login | Login | Public |
| GET | /api/me | Current user | Bearer |
| POST | /api/events | Create event | Organizer |
| GET | /api/events | List events | Public |
| GET | /api/events/{id} | Event details | Public |
| PUT | /api/events/{id} | Update own event | Organizer |
| DELETE | /api/events/{id} | Cancel own event | Organizer |
| POST | /api/events/{id}/rsvp | Create/update RSVP | User |
| PUT | /api/events/{id}/rsvp | Update RSVP | User |
| DELETE | /api/events/{id}/rsvp | Cancel RSVP | User |
| GET | /api/events/{id}/rsvps | Attendee list | Owner |
| GET | /api/events/{id}/analytics | Analytics | Owner |
| POST | /api/events/{id}/announcements | Announcement | Owner |
| GET | /api/events/{id}/announcements | Announcements | Public |
| GET | /api/notifications | User notifications | User |
| PUT | /api/notifications/{id}/read | Mark read | User |
| WS | /ws/events/{id} | Live RSVP stream | Demo channel |

Common status codes: 200 success, 201 created, 400 validation, 401 unauthenticated, 403 unauthorized, 404 missing, 409 conflict/capacity, 500 server error.
