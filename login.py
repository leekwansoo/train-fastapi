from pydantic import BaseModel

class Login(BaseModel):
      
    id: str
    pw: str