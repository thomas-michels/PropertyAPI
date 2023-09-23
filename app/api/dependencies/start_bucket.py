from typing import Callable
from app.api.dependencies.bucket import Bucket
from app.core.configs import get_environment

_env = get_environment()

async def startup():
    print("start")
    if _env.IS_LOCALSTACK:
        Bucket.verify_bucket()

    return None
