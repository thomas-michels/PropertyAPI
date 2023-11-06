from app.core.configs import get_environment, get_logger
import redis

_env = get_environment()
_logger = get_logger(__name__)


class RedisClient:

    def __init__(self) -> None:
        self.__start_conn()

    @property
    def conn(self):
        if self.__conn:
            return self.__conn
        
        raise Exception("Redis not connected")

    def __start_conn(self):
        try:
            self.__conn = redis.StrictRedis(
                host=_env.REDIS_HOST,
                port=_env.REDIS_PORT,
                decode_responses=True
            )
        
        except Exception as error:
            _logger.error(f"Error on start redis connection: {str(error)}")
            self.__conn = None

    def close(self):
        if self.__conn:
            self.__conn.close()

    def __enter__(self):
        """
        Method to start connection
        """
        self.__start_conn()
        _logger.debug("Redis connected")

    def __exit__(self, type, value, traceback):
        """
        Method to close connection
        """
        self.close()
        _logger.debug("Redis connection closed")
