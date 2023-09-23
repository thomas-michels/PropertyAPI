from fastapi import Depends
from app.core.services import PropertyServices
from app.core.db import get_connection, DBConnection
from app.core.db.repositories import PropertyRepository


async def property_composer(
    conn: DBConnection = Depends(get_connection),
) -> PropertyServices:
    property_repository = PropertyRepository(connection=conn)
    service = PropertyServices(property_repository=property_repository)
    return service
