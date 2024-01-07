from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.models import OBS, TeamOBS

import asyncio
from threading import Thread

import uvicorn

from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi

from src.telegram.recognizer import Main
from check.router import router as check_router
from update.router import router as update_router
from delete.router import router as delete_router
from get.router import router as get_router


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Auto Caption System API",
        version="2.5.0",
        description="It is API for Auto Caption System.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


async def start_thread(rec: Main, rtsp: str, host: str, port, password: str):
    rec.rec.connect_obs(host, port, password)
    rec.rec.set_star_title()
    if rtsp == '0':
        await rec.start(4)
    else:
        await rec.start(rtsp)


app = FastAPI(title='Auto Caption System')
app.openapi = custom_openapi

app.include_router(check_router)
app.include_router(update_router)
app.include_router(delete_router)
app.include_router(get_router)

team_to_rec: Dict[int, Main] = {}


@app.post('send_ndi')
async def send_ndi(team_id: int):
    try:
        if team_id in team_to_rec:
            team_to_rec[team_id].rec.send_ndi()
            return {
                'status': 'success',
                'data': None,
                'details': "Титр выведен!"
            }
        else:
            return {
                'status': 'error',
                'data': None,
                'details': "Вы не начали распознавание!"
            }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@app.post('/start_recognition')
async def start_rec(rtsp: str, team_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(
            select(OBS.host,
                   OBS.port,
                   OBS.password
                   ).where(
                TeamOBS.team_id == team_id
            ).join_from(OBS, TeamOBS)
        )
        result = result.all()
        if len(result) == 0:
            return {
                'status': 'error',
                'data': None,
                'details': "Вы не установили OBS config!"
            }
        thread = Thread(target=asyncio.run,
                        args=[
                            start_thread(
                                team_to_rec[team_id],
                                rtsp,
                                result[0][0],
                                result[0][1],
                                result[0][2],
                            )
                        ])
        thread.start()
        return {
                'status': 'success',
                'data': None,
                'details': "Распознавание идёт!"
            }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


@app.post('/end_recognition')
async def end_rec(team_id: int):
    try:
        if team_id in team_to_rec:
            team_to_rec[team_id].rec.set_star_title()
            await team_to_rec[team_id].end()
            return {
                'status': 'success',
                'data': None,
                'details': "Распознавание закончилось!!"
            }
        else:
            return {
                'status': 'error',
                'data': None,
                'details': "Вы не начали распознавание!"
            }
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'details': str(e)
        }


def run():
    thread = Thread(target=uvicorn.run, kwargs={'app': app, 'host': "0.0.0.0", 'port': 4446})
    thread.start()


def add_rec(team_id: int, people: List[str], template: str):
    team_to_rec[team_id] = Main(people, template)


def del_rec(team_id: int):
    team_to_rec.pop(team_id)
