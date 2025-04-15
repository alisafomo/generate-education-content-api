import os
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = os.environ.get('API_KEY_BACKEND')
api_key_header = APIKeyHeader(name='access-token', auto_error=False)


async def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=403,
            detail='Неверный API ключ'
        )
    return api_key_header
