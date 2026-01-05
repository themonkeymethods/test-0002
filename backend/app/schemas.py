from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AccountOut(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime


class MembershipOut(BaseModel):
    id: int
    account_id: int
    user_id: int
    role: str
    created_at: datetime


class UserWithMemberships(UserOut):
    memberships: List[MembershipOut]


class LoginRequest(BaseModel):
    email: str
    password: str
    account_id: Optional[int] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class SwitchAccountRequest(BaseModel):
    account_id: Optional[int] = Field(default=None, description="Account to activate")


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class AuthSession(BaseModel):
    tokens: AuthTokens
    user: UserOut
    active_account: Optional[AccountOut]
    role: Optional[str]
