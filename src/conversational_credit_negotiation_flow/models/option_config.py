from pydantic import BaseModel


class OptionConfig(BaseModel):
    clear_history: bool
