from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_async_session
from src.models import TeamPhoto, UserTeam, OBS, TeamOBS, Template, TeamTemplate

router = APIRouter(
    prefix='/get',
    tags=['Get']
)


@router.get('/people')
async def get_all_people(team_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(
            select(TeamPhoto.photo_path).where(TeamPhoto.team_id == team_id)
        )
        return {
            'status': 'success',
            'data': result.scalars().all(),
            'details': 'People was got!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.get('/templates')
async def get_templates(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(
            select(Template.name)
        )
        return {
            'status': 'success',
            'data': result.scalars().all(),
            'details': 'Templates was got!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.get('/obs_config')
async def get_obs_config(team_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(
            select(OBS.host,
                   OBS.port
                   ).where(
                TeamOBS.team_id == team_id
            ).join_from(OBS, TeamOBS)
        )
        return {
            'status': 'success',
            'data': result.mappings().all(),
            'details': 'OBS config was got!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.get('/team_by_user')
async def get_team_by_user(user_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(
            select(
                UserTeam.team_id
            ).where(UserTeam.id == user_id)
        )
        return {
            'status': 'success',
            'data': result.scalar_one_or_none(),
            'details': 'Team was got by user!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.get('/template_by_team')
async def get_team_by_user(team_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(
            select(
                Template.name
                   ).where(
                TeamTemplate.team_id == team_id
            ).join_from(Template, TeamTemplate)
        )
        return {
            'status': 'success',
            'data': result.scalar_one_or_none(),
            'details': 'Template was get by team!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }
