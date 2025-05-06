from fastapi import Request


async def service_check_middleware(request: Request, call_next):
    return await call_next(request)
