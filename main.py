from fastapi import FastAPI
from app.routers import (
    auth,
    comments,
    post_images,
    posts,
    reservation_participants,
    reservations,
    rooms,
    study_groups,
)

app = FastAPI(title="스터디 플랫폼 API")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(posts.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")
app.include_router(post_images.router, prefix="/api/v1")
app.include_router(rooms.router, prefix="/api/v1")
app.include_router(reservations.router, prefix="/api/v1")
app.include_router(reservation_participants.router, prefix="/api/v1")
app.include_router(study_groups.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "스터디 플랫폼 API 서버가 실행 중입니다."}
