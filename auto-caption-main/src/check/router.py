import re

import face_recognition
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from src.check.constants import NAME_PATTERN, IPV4_PATTERN
from src.database import get_async_session
from src.models import Team

router = APIRouter(
    prefix='/check',
    tags=['Check']
)


@router.get('/name')
async def check_name(name: str):
    try:
        resp = True if re.fullmatch(NAME_PATTERN, name) else False
        return {
            'status': 'success',
            'data': resp,
            'details': 'Name was checked!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.get('/photo')
async def check_photo(path: str):
    try:
        image = face_recognition.load_image_file(path)
        enc = len(face_recognition.face_encodings(image))
        return {
            'status': 'success',
            'data': enc,
            'details': 'Image was checked!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.get('/ipv4')
async def check_ipv4(ip: str):
    try:
        resp = True if re.fullmatch(IPV4_PATTERN, ip) else False
        return {
            'status': 'success',
            'data': resp,
            'details': 'IP was checked!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.get('/port')
async def check_port(port: str):
    try:
        resp = True if re.fullmatch("[0-9]+", port) and 1 <= int(port) <= 65535 else False
        return {
            'status': 'success',
            'data': resp,
            'details': 'Port was checked!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.get('/is_team')
async def check_is_team(name: str, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(
            select(Team.id).where(Team.name == name)
        )
        result = result.scalar_one_or_none()
        resp = False if result is None else True
        return {
            'status': 'success',
            'data': resp,
            'details': 'Team was checked!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@router.get('/password')
async def check_team_password(name: str, password: str, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(
            select(Team.id, Team.password).where(Team.name == name)
        )
        result = result.all()[0]
        resp = True if result[1] == password else False
        return {
            'status': 'success',
            'data': {
                'team_id': result[0],
                'is_password': resp
            },
            'details': 'Password was checked!'
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }
