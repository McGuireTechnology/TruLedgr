import uvicorn
import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from .core.config import settings
from .api.main import api_router

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

if settings.sentry_dsn and not settings.fastapi_debug:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        send_default_pii=settings.sentry_default_pii,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profile_session_sample_rate=settings.sentry_profile_session_sample_rate,
        profile_lifecycle=settings.sentry_profile_lifecycle,
    )

truledgr = app = FastAPI(
    title=settings.fastapi_name,
    debug=settings.fastapi_debug,
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.cors_allowed_origins:
    truledgr.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

truledgr.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        "truledgr.main:app",
        host=settings.uvicorn.host,
        port=settings.uvicorn.port,
        reload=settings.uvicorn.reload
    )
