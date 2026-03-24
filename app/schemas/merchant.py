from pydantic import BaseModel

class MerchantResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class MerchantCreateResponse(BaseModel):
    id: int
    name: str
    api_key: str

    class Config:
        orm_mode = True