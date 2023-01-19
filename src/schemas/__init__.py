from pydantic import BaseModel


class ConfigORM(BaseModel):

    class Config:
        orm_model = True
