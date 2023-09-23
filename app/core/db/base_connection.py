from abc import ABC, abstractmethod


class DBConnection(ABC):

    @abstractmethod
    async def execute(self, sql_statement: str, values: dict = None, many: bool = False):
        """
        Method to execute query
        """

    @abstractmethod
    async def commit(self):
        """
        Method to commit current changes
        """

    @abstractmethod
    async def rollback(self):
        """
        Method to rollback current changes
        """
