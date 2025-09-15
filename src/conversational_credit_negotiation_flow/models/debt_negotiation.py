from typing import Union

from pydantic import BaseModel

from .conversation_classification import ConversationClassification
from .option_config import OptionConfig
from .persona import Persona


class DebtNegotiation(BaseModel):
    persona: Persona
    options: OptionConfig
    conversation_classification: Union[ConversationClassification, None] = None
    negotiation_plan: Union[str, None] = None
