import typing as t
import pydantic as pyd


class IToken(pyd.BaseModel):
    refresh_token: str
    access_token: str
    token_type: str = "bearer"


class IToEncode(pyd.BaseModel):
    user_id: str


class ILogin(pyd.BaseModel):
    email: pyd.EmailStr
    password: t.Optional[str]


class IEmailTokenLogin(pyd.BaseModel):
    access_token: str


class ITokenOut(IToken):
    token_type: str = "Bearer"


class IRefreshToken(pyd.BaseModel):
    refresh_token: str
