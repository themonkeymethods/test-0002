from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status

from app.auth import (
    ACCOUNTS,
    MEMBERSHIPS,
    USERS,
    authenticate_user,
    ensure_can_access_account,
    get_memberships_for_user,
    get_session_from_access_token,
    issue_session,
    refresh_session,
    require_role,
    revoke_session,
    resolve_role,
)
from app.schemas import (
    AccountOut,
    AuthSession,
    AuthTokens,
    LoginRequest,
    MembershipOut,
    RefreshRequest,
    SwitchAccountRequest,
    UserOut,
    UserWithMemberships,
)

app = FastAPI(title="Test App")


def build_tokens(session) -> AuthTokens:
    return AuthTokens(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        token_type="bearer",
        expires_in=int((session.access_expires_at - datetime.utcnow()).total_seconds()),
    )


def get_current_session(authorization: Optional[str] = Header(default=None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be a Bearer token",
        )
    return get_session_from_access_token(token)


def get_current_user(session=Depends(get_current_session)) -> UserOut:
    user = USERS.get(session.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )
    return UserOut(**user.__dict__)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}


@app.post("/auth/login", response_model=AuthSession)
def login(payload: LoginRequest) -> AuthSession:
    user = authenticate_user(payload.email, payload.password)
    active_account_id = payload.account_id
    if active_account_id is not None:
        ensure_can_access_account(user, active_account_id)
    session = issue_session(user, active_account_id)
    active_account = (
        AccountOut(**ACCOUNTS[active_account_id].__dict__)
        if active_account_id in ACCOUNTS
        else None
    )
    return AuthSession(
        tokens=build_tokens(session),
        user=UserOut(**user.__dict__),
        active_account=active_account,
        role=resolve_role(user.id, active_account_id),
    )


@app.post("/auth/logout")
def logout(session=Depends(get_current_session)) -> dict[str, str]:
    revoke_session(session)
    return {"message": "Logged out"}


@app.post("/auth/refresh", response_model=AuthSession)
def refresh(payload: RefreshRequest) -> AuthSession:
    session = refresh_session(payload.refresh_token)
    user = USERS[session.user_id]
    active_account = (
        AccountOut(**ACCOUNTS[session.active_account_id].__dict__)
        if session.active_account_id in ACCOUNTS
        else None
    )
    return AuthSession(
        tokens=build_tokens(session),
        user=UserOut(**user.__dict__),
        active_account=active_account,
        role=resolve_role(user.id, session.active_account_id),
    )


@app.get("/auth/me", response_model=AuthSession)
def me(session=Depends(get_current_session)) -> AuthSession:
    user = USERS[session.user_id]
    active_account = (
        AccountOut(**ACCOUNTS[session.active_account_id].__dict__)
        if session.active_account_id in ACCOUNTS
        else None
    )
    return AuthSession(
        tokens=build_tokens(session),
        user=UserOut(**user.__dict__),
        active_account=active_account,
        role=resolve_role(user.id, session.active_account_id),
    )


@app.post("/auth/switch-account", response_model=AuthSession)
def switch_account(
    payload: SwitchAccountRequest, session=Depends(get_current_session)
) -> AuthSession:
    user = USERS[session.user_id]
    if payload.account_id is not None:
        ensure_can_access_account(user, payload.account_id)
    session.active_account_id = payload.account_id
    active_account = (
        AccountOut(**ACCOUNTS[payload.account_id].__dict__)
        if payload.account_id in ACCOUNTS
        else None
    )
    return AuthSession(
        tokens=build_tokens(session),
        user=UserOut(**user.__dict__),
        active_account=active_account,
        role=resolve_role(user.id, payload.account_id),
    )


@app.get("/admin/accounts", response_model=List[AccountOut])
def list_accounts(session=Depends(get_current_session)) -> List[AccountOut]:
    require_role(session, ["admin"])  # superuser allowed implicitly
    return [AccountOut(**account.__dict__) for account in ACCOUNTS.values()]


@app.get("/admin/users", response_model=List[UserWithMemberships])
def list_users(session=Depends(get_current_session)) -> List[UserWithMemberships]:
    require_role(session, ["admin"])  # superuser allowed implicitly
    users: List[UserWithMemberships] = []
    for user in USERS.values():
        memberships = get_memberships_for_user(user.id)
        users.append(
            UserWithMemberships(
                **user.__dict__,
                memberships=[MembershipOut(**membership.__dict__) for membership in memberships],
            )
        )
    return users


@app.get("/admin/memberships", response_model=List[MembershipOut])
def list_memberships(session=Depends(get_current_session)) -> List[MembershipOut]:
    require_role(session, ["admin"])
    return [MembershipOut(**membership.__dict__) for membership in MEMBERSHIPS]
