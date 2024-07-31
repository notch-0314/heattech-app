from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    user_name: str
    email: str
    password: str

class UserInDB(User):
    hashed_password: str
