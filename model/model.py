from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Message(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    message: str = Field(...)
    queue_number: int = Field(0)


class ReplicationRequest(BaseModel):
    message: Message
    write_concern: int = Field(ge=1)
