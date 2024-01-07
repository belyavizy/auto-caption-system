import os
import re
import shutil

import face_recognition
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.database import get_async_session
from src.update.utils import create_path_by_name
from src.models import TeamPhoto, OBS, TeamOBS, TeamTemplate, UserTeam, Team
import src.app as app

router = APIRouter(
    prefix='/update',
    tags=['Update']
)


@router.post('/photo')
async def update_photo(path: str, name: str, team_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        fullname, role = name.split('-')
        name = '_'.join(fullname.split()) + '-' + role
        result = await session.execute(select(TeamPhoto.photo_path).where(TeamPhoto.team_id == team_id))
        people = result.scalars().all()

        count = 0
        for el in people:
            if re.search(name, el):
                count += 1

        new_path = create_path_by_name(name, team_id, count)
        abs_path = os.path.abspath(new_path)
        shutil.move(path, abs_path)

        team_photo = TeamPhoto(team_id=team_id, photo_path=abs_path)        # noqa
        session.add(team_photo)

        print(app.team_to_rec)
        if team_id in app.team_to_rec:
            file = face_recognition.load_image_file(path)
            app.team_to_rec[team_id].rec.add_photo(fullname, role, file)

        await session.flush()
        await session.commit()

        return {
            'status': 'success',
            'data': None,
            'details': 'Photo was added!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.post('/obs_config')
async def update_obs_config(host: str, port: int, password: str,
                            team_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(TeamOBS.obs_id).where(TeamOBS.team_id == team_id))
        result = result.scalar_one_or_none()
        if result is None:
            stmt = OBS(host=host, port=port, password=password)  # noqa
            session.add(stmt)
            await session.flush()
            await session.refresh(stmt)
            obs_id = stmt.id
            stmt2 = TeamOBS(team_id=team_id, obs_id=obs_id)  # noqa
            session.add(stmt2)
            await session.flush()
            await session.commit()
        else:
            await session.execute(
                update(OBS).where(OBS.id == result).values(host=host, port=port, password=password)
            )
            await session.commit()
        return {
            'status': 'success',
            'data': None,
            'details': 'OBS Config was updated!'
        }
    except Exception() as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.post('/template_team')
async def update_template_for_team(team_id: int, template_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        await session.execute(
            update(TeamTemplate).where(TeamTemplate.team_id == team_id).values(template_id=template_id)
        )
        await session.commit()
        return {
            'status': 'success',
            'data': None,
            'details': 'Template and team was linked!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.post('/user')
async def update_user(team_id: int, user_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(UserTeam.id).where(UserTeam.id == user_id))
        result = result.scalar_one_or_none()
        if result is None:
            stmt = UserTeam(id=user_id, team_id=team_id)   # noqa
            session.add(stmt)
            await session.flush()
            await session.commit()
        else:
            await session.execute(
                update(UserTeam).where(UserTeam.id == result).values(team_id=team_id)
            )
            await session.commit()
        return {
            'status': 'success',
            'data': None,
            'details': 'User was updated!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.post('/add_team')
async def add_team(user_id: int, name: str, password: str, session: AsyncSession = Depends(get_async_session)):
    try:
        stmt = Team(name=name, password=password)   # noqa
        session.add(stmt)
        await session.flush()
        await session.refresh(stmt)
        print(stmt.id)
        result = await session.execute(select(UserTeam.id).where(UserTeam.id == user_id))
        result = result.scalar_one_or_none()
        if result is None:
            stmt2 = UserTeam(id=user_id, team_id=stmt.id)  # noqa
            session.add(stmt2)
            await session.flush()
            await session.commit()
        else:
            await session.execute(
                update(UserTeam).where(UserTeam.id == result).values(team_id=stmt.id)
            )
        stmt2 = TeamTemplate(team_id=stmt.id, template_id=0)   # noqa
        session.add(stmt2)
        await session.flush()
        await session.commit()
        return {
            'status': 'success',
            'data': None,
            'details': 'Team was added!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }
