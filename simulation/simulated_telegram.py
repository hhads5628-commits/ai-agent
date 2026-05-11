from dataclasses import dataclass, field
from typing import List


@dataclass
class FakeMessage:
    text: str
    replies: List[str] = field(default_factory=list)

    async def reply_text(self, text: str, reply_markup=None):
        self.replies.append(text)


@dataclass
class FakeChat:
    id: int


@dataclass
class FakeUpdate:
    text: str
    chat_id: int

    def __post_init__(self):
        self.message = FakeMessage(self.text)
        self.effective_chat = FakeChat(self.chat_id)
