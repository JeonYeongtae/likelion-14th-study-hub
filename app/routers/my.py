"""
My Router — 마이페이지 통합 활동 기록 API

GET /my/posts         내가 쓴 게시글
GET /my/comments      내가 쓴 댓글
GET /my/likes         내가 좋아요 누른 게시글
GET /my/applications  내가 신청한 스터디 목록 (그룹 정보 포함)
GET /my/groups        내가 만든(조장인) 그룹 + 신청자 현황
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.repositories import application_repo, comment_repo, like_repo, post_repo, study_group_repo
from app.schemas.application import MyApplicationResponse
from app.schemas.chat import ChatRoomListItem
from app.schemas.comment import CommentResponse
from app.schemas.post import PostResponse
from app.schemas.study_group import ApplicationSummary, StudyGroupDetailResponse
from app.services import chat_service

router = APIRouter(prefix="/my", tags=["My Page"])


@router.get("/posts", response_model=list[PostResponse])
def my_posts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내가 쓴 게시글 목록 (최신순)"""
    return post_repo.get_posts_by_user(db, current_user.id)


@router.get("/comments", response_model=list[CommentResponse])
def my_comments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내가 쓴 댓글 목록 (최신순, post_id + post_title 포함)"""
    comments = comment_repo.get_comments_by_user(db, current_user.id)
    result = []
    for c in comments:
        post = post_repo.get_post_by_id(db, c.post_id)
        result.append(CommentResponse(
            id=c.id,
            post_id=c.post_id,
            post_title=post.title if post else "삭제된 게시글",
            user_id=c.user_id,
            nickname=c.nickname,
            parent_comment_id=c.parent_comment_id,
            content=c.content,
            created_at=c.created_at,
            updated_at=c.updated_at,
        ))
    return result


@router.get("/likes", response_model=list[PostResponse])
def my_likes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내가 좋아요 누른 게시글 목록"""
    likes = like_repo.get_likes_by_user(db, current_user.id)
    return [like.post for like in likes]


@router.get("/applications", response_model=list[MyApplicationResponse])
def my_applications(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내가 신청한 스터디 목록 (상태 + 그룹 정보 포함, 최신순)"""
    apps = application_repo.get_applications_by_user(db, current_user.id)
    result = []
    for app in apps:
        group = study_group_repo.get_group_by_id(db, app.group_id)
        result.append(MyApplicationResponse(
            id=app.id,
            group_id=app.group_id,
            applicant_id=app.applicant_id,
            status=app.status,
            message=app.message,
            created_at=app.created_at,
            group_title=group.title if group else "삭제된 그룹",
            group_status=group.status if group else "종료",
        ))
    return result


@router.get("/groups", response_model=list[StudyGroupDetailResponse])
def my_groups(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내가 만든(조장인) 스터디 그룹 목록 + 신청자 현황 (최신순)"""
    groups = study_group_repo.get_groups_by_leader(db, current_user.id)
    result = []
    for group in groups:
        apps = application_repo.get_applications_by_group(db, group.id)
        detail = StudyGroupDetailResponse.model_validate(group)
        detail.applications = [ApplicationSummary.model_validate(a) for a in apps]
        result.append(detail)
    return result


@router.get("/chats", response_model=list[ChatRoomListItem])
def my_chats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """내가 속한 채팅방 목록 (확정된 그룹만 — status='종료')"""
    return chat_service.get_my_chat_rooms(db, current_user.id)
