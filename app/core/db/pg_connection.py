from psycopg.connection_async import AsyncConnection
from psycopg.rows import dict_row
from .base_connection import DBConnection
from app.core.configs import get_environment

_env = get_environment()


class PGConnection(DBConnection):

    def __init__(self, conn: AsyncConnection) -> None:
        self.conn = conn
        self.cursor = None

    async def execute(self, sql_statement: str, values: dict = None, many: bool = False):
        sql = sql_statement.replace("public", _env.ENVIRONMENT)

        self.cursor = self.conn.cursor(row_factory=dict_row)
        await self.cursor.execute(sql, values)
        return await self.cursor.fetchall() if many else await self.cursor.fetchone()

    async def commit(self):
        await self.conn.commit()

    async def rollback(self):
        await self.conn.rollback()
