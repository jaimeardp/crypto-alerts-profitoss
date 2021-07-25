import aioredis
import os
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
from typing import Optional

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi_cache.coder import Coder, JsonCoder


app = FastAPI()



@cache()
async def get_cache():
    return 1

def my_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    prefix = FastAPICache.get_prefix()
    cache_key = f"{prefix}:{namespace}:{func.__module__}:{func.__name__}:{args}:{kwargs}"
    return cache_key


@app.get("/")
@cache( expire=120, coder=JsonCoder, key_builder=my_key_builder)
async def index(request: Request, response: Response):
    return dict(hello="world")


@app.on_event("startup")
async def startup():
    redis =  aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

