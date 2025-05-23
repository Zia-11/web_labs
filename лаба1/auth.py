# auth.py
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()  # схема для “Bearer <token>”

fake_users_db = {
    "admin_token": {"username": "admin", "is_admin": True},
    "user_token": {"username": "user", "is_admin": False}
}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    token = credentials.credentials
    user = fake_users_db.get(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )
    return user


def is_authenticated(user: dict = Depends(get_current_user)):
    return user


def is_admin_user(user: dict = Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется доступ администратора"
        )
    return user
