from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_token_credentials
from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_reset_token,
    get_password_hash,
    hash_reset_token,
    jwt_payload_safe,
    verify_password,
)
from app.models.user_model import PasswordResetToken, RevokedToken, User
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo ya está registrado")
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role="cliente",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada",
        )
    token, jti, expire = create_access_token(user_id=user.id, role=user.role)
    now = datetime.now(timezone.utc)
    expires_in = max(0, int((expire - now).total_seconds()))
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: Session = Depends(get_db),
    token: str = Depends(get_token_credentials),
) -> None:
    payload = jwt_payload_safe(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    jti = payload.get("jti")
    exp_ts = payload.get("exp")
    if not jti or exp_ts is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    if db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
        return None
    expires_at = datetime.fromtimestamp(int(exp_ts), tz=timezone.utc)
    db.add(
        RevokedToken(
            jti=jti,
            expires_at=expires_at,
            revoked_at=datetime.now(timezone.utc),
        )
    )
    db.commit()


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> ForgotPasswordResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    msg = "Si el correo existe en el sistema, recibirás instrucciones para restablecer la contraseña."
    if not user:
        return ForgotPasswordResponse(message=msg, debug_token=None)
    raw = generate_reset_token()
    th = hash_reset_token(raw)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=th,
            expires_at=expires_at,
        )
    )
    db.commit()
    debug = raw if settings.DEBUG_RESET_TOKEN else None
    return ForgotPasswordResponse(message=msg, debug_token=debug)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> None:
    th = hash_reset_token(payload.token)
    now = datetime.now(timezone.utc)
    row = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == th,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        .first()
    )
    if not row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado",
        )
    user = db.query(User).filter(User.id == row.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido")
    user.hashed_password = get_password_hash(payload.new_password)
    row.used_at = now
    db.commit()
