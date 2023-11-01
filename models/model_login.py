from typing import Optional
from pydantic import BaseModel

class Login(BaseModel):
      
    id: Optional[str] = None
    pw: Optional[str] = None
    user: Optional[str] = None
    email: Optional[str] = None