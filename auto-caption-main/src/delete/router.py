import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from src.database import get_async_session
from src.models import TeamPhoto

router = APIRouter(
    prefix='/delete',
    tags=['Delete']
)


# @router.delete('/team')
# async def delete_team(name: str, session: AsyncSession = Depends(get_async_session)):
#     Неверно
#     try:
#         await session.execute(
#             delete(Team).where(Team.name == name)
#         )
#         await session.commit()
#         return {
#             'status': 'error',
#             'data': None,
#             'details': 'Team was deleted!'
#         }
#     except Exception as e:
#         return {
#             'status': 'error',
#             'data': None,
#             'details': str(e)
#         }


@router.delete('/photo')
async def delete_photo(path: str, session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute(
            delete(TeamPhoto).where(TeamPhoto.photo_path == path)
        )
        await session.commit()
        os.remove(path)
        # self.rec.rec.del_photo(idx)       TO DO
        return {
            'status': 'success',
            'data': None,
            'details': 'Photo was deleted!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }
