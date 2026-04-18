from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    auth,
    chat,
    comments,
    my,
    notifications,
    post_images,
    posts,
    reservation_participants,
    reservations,
    rooms,
    study_groups,
    users,
)

app = FastAPI(title="스터디 플랫폼 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(my.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")
app.include_router(post_images.router, prefix="/api/v1")
app.include_router(rooms.router, prefix="/api/v1")
app.include_router(reservations.router, prefix="/api/v1")
app.include_router(reservation_participants.router, prefix="/api/v1")
app.include_router(study_groups.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "스터디 플랫폼 API 서버가 실행 중입니다."}
