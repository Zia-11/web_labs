from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# экземпляр схме аутентификации
bearer_scheme = HTTPBearer()

# наша бд
users_db = {
    "admin_token": {"username": "admin", "is_admin": True},
    "user_token": {"username": "user", "is_admin": False}
}

# проверка на юзера


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
):
    # достаем токен
    token = credentials.credentials
    # если есть такой токен получаем данные пользователя
    user = users_db.get(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )
    return user

# проверка на авторизованность


def is_authenticated(user: dict = Depends(get_current_user)):
    return user

# проверка на админа


def is_admin_user(user: dict = Depends(get_current_user)):
    # если не админ - доступ запрещен
    if not user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется доступ администратора"
        )
    return user
