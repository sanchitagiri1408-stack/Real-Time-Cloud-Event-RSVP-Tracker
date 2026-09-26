from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections = defaultdict(set)

    async def connect(self, event_id: int, websocket: WebSocket):
        await websocket.accept()
        self.connections[event_id].add(websocket)

        print(
            f"[WS] CONNECTED event={event_id} "
            f"connections={len(self.connections[event_id])}"
        )

    def disconnect(self, event_id: int, websocket: WebSocket):
        self.connections[event_id].discard(websocket)

        print(
            f"[WS] DISCONNECTED event={event_id} "
            f"connections={len(self.connections[event_id])}"
        )

    async def broadcast(self, event_id: int, message: dict):
        connections = list(self.connections[event_id])

        print(
            f"[WS] BROADCAST event={event_id} "
            f"connections={len(connections)} "
            f"message={message}"
        )

        dead = []

        for ws in connections:
            try:
                await ws.send_json(message)

                print(
                    f"[WS] SENT event={event_id} "
                    f"message_type={message.get('type')}"
                )

            except Exception as e:
                print(
                    f"[WS] SEND FAILED event={event_id}: {e}"
                )
                dead.append(ws)

        for ws in dead:
            self.disconnect(event_id, ws)


manager = ConnectionManager()