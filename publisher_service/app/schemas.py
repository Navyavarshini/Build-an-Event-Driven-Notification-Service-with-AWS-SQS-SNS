from pydantic import BaseModel, EmailStr

class EventPayload(BaseModel):
    eventType: str
    recipient: EmailStr
    data: dict
