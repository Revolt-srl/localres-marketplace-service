from functools import wraps
from fastapi import HTTPException
import os


def async_user_authorize(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        token = kwargs.get("token")
        if token is None:
            raise HTTPException(status_code=401, detail="Unauthenticated")
        if token.credentials != os.environ.get("CLIENT_API_TOKEN"):
            raise HTTPException(status_code=403, detail="Invalid token")
        return await fn(*args, **kwargs)

    return wrapper


def user_authorize(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = kwargs.get("token")
        if token is None:
            raise HTTPException(status_code=401, detail="Unauthenticated")
        allowed_tokens = [
            os.environ.get("CLIENT_API_TOKEN"),
            os.environ.get("ADMIN_API_TOKEN")
        ]
        if token.credentials not in allowed_tokens:
            raise HTTPException(status_code=403, detail="Invalid token")
        return fn(*args, **kwargs)

    return wrapper


def async_admin_authorize(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        token = kwargs.get("token")
        if token is None:
            raise HTTPException(status_code=401, detail="Unauthenticated")
        allowed_tokens = [
            os.environ.get("CLIENT_API_TOKEN"),
            os.environ.get("ADMIN_API_TOKEN")
        ]
        if token.credentials not in allowed_tokens:
            raise HTTPException(status_code=403, detail="Invalid token")
        return await fn(*args, **kwargs)

    return wrapper


def admin_authorize(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = kwargs.get("token")
        if token is None:
            raise HTTPException(status_code=401, detail="Unauthenticated")
        if token.credentials != os.environ.get("ADMIN_API_TOKEN"):
            raise HTTPException(status_code=403, detail="Invalid token")
        return fn(*args, **kwargs)

    return wrapper
