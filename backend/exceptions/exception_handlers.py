from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from backend.exceptions.custom_exceptions import NotFoundException, BadRequestException, UnauthorizedException
from backend.routers.models.base import BaseMessageResponse


async def handle_bad_request_exception(_: Request, ex: BadRequestException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=BaseMessageResponse(
            message=ex.message
        ).model_dump()
    )


async def handle_not_found_exception(_: Request, ex: NotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=BaseMessageResponse(
            message=ex.message
        ).model_dump()
    )

async def handle_unauthorized_exception(_: Request, ex: UnauthorizedException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=BaseMessageResponse(
            message=ex.message
        ).model_dump()
    )

async def handle_request_validation_exception(_: Request, ex: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=BaseMessageResponse(
            message=", ".join([f'{".".join(map(str, err["loc"]))}: {err["msg"]}' for err in ex.errors()])
        ).model_dump()
    )

def register_exception_handling(app: FastAPI):
    app.add_exception_handler(NotFoundException, handle_not_found_exception)
    app.add_exception_handler(BadRequestException, handle_bad_request_exception)
    app.add_exception_handler(UnauthorizedException, handle_unauthorized_exception)
    app.add_exception_handler(RequestValidationError, handle_request_validation_exception)
