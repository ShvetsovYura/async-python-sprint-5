import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination

from api.v1 import files, service, users
from core.config import app_settings
from core.logger import logger

app = FastAPI(title=app_settings.app_title,
              docs_url='/api/openapi',
              openapi_url='/api/openapi.json',
              default_response_class=ORJSONResponse,
              redoc_url=None)

prefix_ = '/api/v1'

app.include_router(files.router, prefix=prefix_, tags=['files'])
app.include_router(users.router, prefix=prefix_, tags=['users'])
app.include_router(service.router, prefix=prefix_, tags=['service'])

add_pagination(app)

if __name__ == '__main__':

    logger.info('Start server.')
    uvicorn.run(
        'app:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
    )
# Николай, большое спасибо за замечания!
# Исправил
# Большое спасибо за best practices в тестах - многое не знал
