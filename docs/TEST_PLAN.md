# Test plan

| ID | Scenario | Expected result |
|---|---|---|
| T01 | Register | 201 + token |
| T02 | Duplicate registration | 409 |
| T03 | Login | 200 + token |
| T04 | Organizer creates event | 201 |
| T05 | Attendee creates event | 403 |
| T06 | Get event | 200 |
| T07 | Valid RSVP | 200 |
| T08 | Duplicate RSVP | Updates existing record |
| T09 | GOING -> MAYBE | Counts change |
| T10 | MAYBE -> GOING | Counts change |
| T11 | Cancel RSVP | Record removed |
| T12 | Registration deadline | Production validation must reject after deadline |
| T13 | Capacity reached | FULL / 409 |
| T14 | Simultaneous final seat | Must be atomic in production |
| T15 | Waitlist | FIFO record created |
| T16 | Announcement | Notifications created |
| T17 | Unauthorized event edit | 403 |
| T18 | Unauthorized RSVP edit | User-scoped |
| T19 | Realtime update | WebSocket message received |
| T20 | Analytics | Counts/utilization returned |
| T21 | DB failure | Graceful error + logs |
| T22 | WebSocket failure | Client can reconnect |
| T23 | Token expiry | 401 |
| T24 | Event cancellation | Status CANCELLED |
