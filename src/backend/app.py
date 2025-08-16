from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, chama, user
from routers import mpesa
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(chama.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(mpesa.router, prefix="/api")

app.mount("/static", StaticFiles(directory="static"), name="static")