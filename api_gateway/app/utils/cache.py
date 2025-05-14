import json
from datetime import datetime
from functools import wraps
from typing import Annotated, Any
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.responses import JSONResponse, Response

from app.repositories.redis_repository import RedisRepository
from app.containers.container import Container


def custom_serializer(obj: Any) -> str:
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        return str(obj)


def get_redis_cache(hash_name: str, expiration_time: int):
    def decorator(func):
        @wraps(func)
        @inject
        async def wrapper(
            *args,
            redis_repository: Annotated[
                RedisRepository, Depends(Provide[Container.redis_repository])
            ] = None,
            **kwargs,
        ):
            try:
                is_redis_available = await redis_repository.ping()
                if not is_redis_available:
                    print("Redis is not available, skipping cache")
                    return await func(*args, **kwargs)
            except Exception as e:
                print(f"Error checking Redis connection: {e}")
                return await func(*args, **kwargs)

            request = None
            service_name = None
            path = None

            for arg in args:
                if hasattr(arg, "method"):
                    request = arg
                    print(f"Found request in args: method={request.method}")

            if "service_name" in kwargs:
                service_name = kwargs["service_name"]
                print(f"Found service_name in kwargs: {service_name}")
            if "path" in kwargs:
                path = kwargs["path"]
                print(f"Found path in kwargs: {path}")

            if request and request.method != "GET":
                print(f"Skipping cache for non-GET method: {request.method}")
                return await func(*args, **kwargs)

            if request and service_name and path:
                query_params = ""
                if hasattr(request, "query_params"):
                    query_params = str(request.query_params)
                cache_key = f"{hash_name}:{service_name}:{path}:{query_params}"
            else:
                parts = []
                if service_name:
                    parts.append(service_name)
                if path:
                    parts.append(path)
                cache_key = f"{hash_name}:{':'.join(parts) or 'default'}"

            print(f"Cache key: {cache_key}")

            try:
                print(f"Attempting to get data from cache with key: {cache_key}")
                cached_value = await redis_repository.get(cache_key)

                if cached_value:
                    print(f"Cache HIT for key: {cache_key}")
                    try:
                        deserialized_data = json.loads(cached_value)
                        print(f"Successfully deserialized cached data")
                        return deserialized_data
                    except json.JSONDecodeError as e:
                        print(
                            f"Error deserializing cached data: {e}, returning as raw string"
                        )
                        return cached_value
                else:
                    print(f"Cache MISS for key: {cache_key}")

                print(f"Executing original function...")
                result = await func(*args, **kwargs)
                print(f"Function executed, result type: {type(result)}")

                cache_data = None

                if isinstance(result, JSONResponse):
                    print(f"Extracting JSON data from JSONResponse for caching")
                    try:
                        cache_data = result.body.decode("utf-8")
                        print(f"Successfully extracted JSON data from response")
                    except Exception as e:
                        print(f"Failed to extract JSON from response: {e}")

                elif isinstance(result, Response):
                    print(f"Response is not JSONResponse, skipping cache storage")
                    return result
                elif isinstance(result, dict) or isinstance(result, list):
                    cache_data = json.dumps(result, default=custom_serializer)
                    print(f"Result is directly serializable object")
                else:
                    print(f"Result is not JSON-serializable, converting to string")
                    try:
                        cache_data = str(result)
                    except Exception as e:
                        print(f"Failed to convert result to string: {e}")
                        return result

                if not cache_data:
                    print(f"No cacheable data extracted, skipping cache storage")
                    return result

                try:

                    success = await redis_repository.set(
                        cache_key,
                        cache_data,
                        ttl=expiration_time,
                    )
                    print(f"Cache save result: {success}")

                    print(f"Verifying cache save...")
                    verification = await redis_repository.get(cache_key)

                    if verification:
                        print(f"Verification successful - data cached")
                    else:
                        print(f"Verification failed - data not cached")

                except Exception as e:
                    print(f"Error during cache saving: {e}")

                return result
            except Exception as e:
                print(f"Error in cache operations: {e}")
                return await func(*args, **kwargs)

        return wrapper

    return decorator
