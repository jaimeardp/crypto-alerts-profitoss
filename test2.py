import json
import os
import aioredis
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Depends

# Upload CSV file
#from parse_csv import convertBytesToString

# Cryptomarket API
from requests import Request, Response,Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


from fastapi_cache import caches, close_caches
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.redis import CACHE_KEY, RedisCacheBackend
from fastapi_cache.decorator import cache
from fastapi_cache.coder import Coder, JsonCoder

from dotenv import load_dotenv
load_dotenv()

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
parameters = {
  'start':'1',
  'limit':'3',
  'convert':'USD'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': os.environ["KEY_CMC"],
}

session = Session()
session.headers.update(headers)

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


app = FastAPI()

@app.get("/")
def getName():
    return { "Name": "Jaime"}

"""@app.post("/csv/")
async def parsecsv(file: UploadFile = File(...)):  
    contents = await file.read()
    json_string = convertBytesToString(contents)
    return {"file_contents": json_string}
"""

def redis_cache():
    return caches.get(CACHE_KEY)

@app.get("/crypto/")
#@cache( expire=120, coder=JsonCoder, key_builder=my_key_builder)
async def cryptodata(
    cache: RedisCacheBackend = Depends(redis_cache), id: str = ''
):
    data = {}
    try:
        in_cache = await cache.get(id)
        if not in_cache:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            print("Successfully request cmc!")
            await cache.set(id, data, 5)
            return {"crypto_data": data}
        return {"crypto_data": in_cache}
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    
    


@app.on_event("startup")
async def startup():
    redis =  aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")