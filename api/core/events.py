from typing import Callable

from fastapi import FastAPI
from loguru import logger

from api.core.config import DATABASE


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        logger.info("Connecting to database")

        app.state.database = DATABASE
        await app.state.database.connect()

        logger.info("Database connection established")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    @logger.catch
    async def stop_app() -> None:
        logger.info("Disconnecting from database")

        await app.state.database.disconnect()
        logger.info("Disconnected database connection")

    return stop_app