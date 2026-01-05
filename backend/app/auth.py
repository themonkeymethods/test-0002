from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import secrets
from typing import Dict, List, Optional

from fastapi import HTTPException, status

ACCESS_TOKEN_TTL = timedelta(minutes=30)
REFRESH_TOKEN_TTL = timedelta(days=7)


@dataclass
class AccountRecord:
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime


@dataclass
class UserRecord:
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    password: str
    created_at: datetime


@dataclass
class MembershipRecord:
    id: int
    account_id: int
    user_id: int
    role: str
    created_at: datetime


@dataclass
class SessionRecord:
    user_id: int
    active_account_id: Optional[int]
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


ACCOUNTS: Dict[int, AccountRecord] = {
    1: AccountRecord(
        id=1,
        name="Acme Corp",
        email="billing@acme.test",
        is_active=True,
        created_at=datetime.utcnow(),
    ),
    2: AccountRecord(
        id=2,
        name="Northwind Traders",
        email="finance@northwind.test",
        is_active=True,
        created_at=datetime.utcnow(),
    ),
}

USERS: Dict[int, UserRecord] = {
    1: UserRecord(
        id=1,
        email="superuser@test.com",
        full_name="Super User",
        is_active=True,
        is_superuser=True,
        password="supersecret",
        created_at=datetime.utcnow(),
    ),
    2: UserRecord(
        id=2,
        email="admin@acme.test",
        full_name="Alex Admin",
        is_active=True,
        is_superuser=False,
        password="adminpass",
        created_at=datetime.utcnow(),
    ),
    3: UserRecord(
        id=3,
        email="editor@northwind.test",
        full_name="Casey Editor",
        is_active=True,
        is_superuser=False,
        password="editorpass",
        created_at=datetime.utcnow(),
    ),
}

MEMBERSHIPS: List[MembershipRecord] = [
    MembershipRecord(
        id=1,
        account_id=1,
        user_id=2,
        role="admin",
        created_at=datetime.utcnow(),
    ),
    MembershipRecord(
        id=2,
        account_id=1,
        user_id=3,
        role="member",
        created_at=datetime.utcnow(),
    ),
    MembershipRecord(
        id=3,
        account_id=2,
        user_id=3,
        role="admin",
        created_at=datetime.utcnow(),
    ),
]

SESSIONS_BY_ACCESS: Dict[str, SessionRecord] = {}
SESSIONS_BY_REFRESH: Dict[str, SessionRecord] = {}


def authenticate_user(email: str, password: str) -> UserRecord:
    for user in USERS.values():
        if user.email == email and user.password == password:
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive",
                )
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )


def issue_session(user: UserRecord, active_account_id: Optional[int]) -> SessionRecord:
    now = datetime.utcnow()
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(40)
    session = SessionRecord(
        user_id=user.id,
        active_account_id=active_account_id,
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=now + ACCESS_TOKEN_TTL,
        refresh_expires_at=now + REFRESH_TOKEN_TTL,
    )
    SESSIONS_BY_ACCESS[access_token] = session
    SESSIONS_BY_REFRESH[refresh_token] = session
    return session


def revoke_session(session: SessionRecord) -> None:
    SESSIONS_BY_ACCESS.pop(session.access_token, None)
    SESSIONS_BY_REFRESH.pop(session.refresh_token, None)


def refresh_session(refresh_token: str) -> SessionRecord:
    session = SESSIONS_BY_REFRESH.get(refresh_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid",
        )
    if session.refresh_expires_at < datetime.utcnow():
        revoke_session(session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )
    user = USERS.get(session.user_id)
    if not user:
        revoke_session(session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )
    revoke_session(session)
    return issue_session(user, session.active_account_id)


def get_session_from_access_token(access_token: str) -> SessionRecord:
    session = SESSIONS_BY_ACCESS.get(access_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is invalid",
        )
    if session.access_expires_at < datetime.utcnow():
        revoke_session(session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
        )
    return session


def get_memberships_for_user(user_id: int) -> List[MembershipRecord]:
    return [membership for membership in MEMBERSHIPS if membership.user_id == user_id]


def resolve_role(user_id: int, account_id: Optional[int]) -> Optional[str]:
    if account_id is None:
        return None
    for membership in MEMBERSHIPS:
        if membership.user_id == user_id and membership.account_id == account_id:
            return membership.role
    return None


def ensure_can_access_account(user: UserRecord, account_id: int) -> None:
    if user.is_superuser:
        return
    role = resolve_role(user.id, account_id)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to the selected account",
        )


def require_role(session: SessionRecord, required_roles: List[str]) -> None:
    user = USERS.get(session.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )
    if user.is_superuser:
        return
    role = resolve_role(user.id, session.active_account_id)
    if role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
