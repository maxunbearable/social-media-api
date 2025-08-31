from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
import logging
from api.models.post import Comment, CommentInput, UserPost, UserPostInput, UserPostWithComments
from api.database import post_table, comment_table, database
from api.models.user import User
from api.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

async def find_post(post_id: int) -> UserPost | None:
    logger.info(f"Finding post with id: {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.info(query)
    return await database.fetch_one(query)

@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentInput, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info(f"Creating comment for post_id: {comment.post_id}")
    post_id = comment.post_id
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    data = { **comment.model_dump(), "user_id": current_user.id }
    query = comment_table.insert().values(data)
    logger.debug(query)
    comment_id = await database.execute(query)
    return {**data, "id": comment_id}

@router.get("/post/{post_id}/comments", response_model=list[Comment])
async def get_comments(post_id: int):
    logger.info(f"Getting comments for post_id: {post_id}")
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)

@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostInput, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info(f"Creating post: {post}")
    data = { **post.model_dump(), "user_id": current_user.id }
    query = post_table.insert().values(data)
    logger.debug(query)
    post_id = await database.execute(query)
    return {**data, "id": post_id}

@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    logger.info(f"Getting post with comments for post_id: {post_id}")
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = await get_comments(post_id)
    return UserPostWithComments(post=post, comments=comments)

@router.get("/posts", response_model=list[UserPost])
async def get_posts():
    logger.info("Getting all posts")
    query = post_table.select()
    logger.info(query)
    return await database.fetch_all(query)