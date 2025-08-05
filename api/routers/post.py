from fastapi import APIRouter, HTTPException
from api.models.post import Comment, CommentInput, UserPost, UserPostInput, UserPostWithComments
from api.database import post_table, comment_table, database

router = APIRouter()

async def find_post(post_id: int) -> UserPost | None:
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)

@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentInput):
    post_id = comment.post_id
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    data = comment.model_dump()
    query = comment_table.insert().values(data)
    comment_id = await database.execute(query)
    return {**data, "id": comment_id}

@router.get("/post/{post_id}/comments", response_model=list[Comment])
async def get_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)

@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostInput):
    data = post.model_dump()
    query = post_table.insert().values(data)
    post_id = await database.execute(query)
    return {**data, "id": post_id}

@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = await get_comments(post_id)
    return UserPostWithComments(post=post, comments=comments)

@router.get("/posts", response_model=list[UserPost])
async def get_posts():
    query = post_table.select()
    return await database.fetch_all(query)