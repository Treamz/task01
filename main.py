import uvicorn
from fastapi import FastAPI

import os

from routes import root
from db.core import create_delete_db
from settings import settings

app = FastAPI(docs_url=None, redoc_url=None)

@app.on_event("startup")
def startup():
    if not os.path.exists(settings.db_path):
        create_delete_db()

app.include_router(root, prefix='/api')



if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True, host='0.0.0.0')