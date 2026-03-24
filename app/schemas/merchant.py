from pydantic import BaseModel

class MerchantResponse(BaseModel):
    id: int
    name: str
