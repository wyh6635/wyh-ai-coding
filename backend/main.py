from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os

from routers.auth import router as auth_router
from routers.students import router as students_router
from routers.subjects import router as subjects_router
from routers.scores import router as scores_router
from routers.dashboard import router as dashboard_router
from routers.users import router as users_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'app.log'), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

app = FastAPI(
    title='校园信息管理系统 API',
    version='1.0.0',
    description='学生管理系统后端API服务'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={'code': 500, 'msg': '服务器内部错误', 'data': None}
    )


@app.get('/')
def root():
    return {
        'code': 200,
        'msg': '欢迎使用校园信息管理系统 API',
        'data': {'version': '1.0.0'}
    }


@app.get('/health')
def health_check():
    return {'code': 200, 'msg': 'OK', 'data': {'status': 'healthy'}}


app.include_router(auth_router)
app.include_router(students_router)
app.include_router(subjects_router)
app.include_router(scores_router)
app.include_router(dashboard_router)
app.include_router(users_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )