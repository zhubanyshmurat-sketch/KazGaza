from fastapi import APIRouter

from app.api.routes import admins, application_types, applications, auth, bot, dashboard, settings, ws

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(applications.router)
api_router.include_router(admins.router)
api_router.include_router(dashboard.router)
api_router.include_router(settings.router)
api_router.include_router(application_types.router)
api_router.include_router(bot.router)
api_router.include_router(ws.router)
