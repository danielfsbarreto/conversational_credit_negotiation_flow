from pydantic import BaseModel


class Persona(BaseModel):
    name: str
    age: int
    cellphone: str
    gender: str
    age: int
    debt: int
    yearly_revenue: int
