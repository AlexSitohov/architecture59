from fastapi import Request


async def jwt_auth_middleware(request: Request, call_next):
    response = await call_next(request)
    return response
