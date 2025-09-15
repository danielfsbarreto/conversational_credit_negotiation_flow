from typing import List, Union

from pydantic import BaseModel

from .debt_negotiation import DebtNegotiation
from .message import Message


class FlowState(BaseModel):
    debt_negotiation: Union[DebtNegotiation, None] = None
    user_message: Union[Message, None] = None
    assistant_message: Union[Message, None] = None
    history: List[Message] = []
