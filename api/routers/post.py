from fastapi import APIRouter, HTTPException
from api.models.post import Comment, CommentInput, UserPost, UserPostInput, UserPostWithComments

router = APIRouter()

post_table = {}
comment_table = {}

def find_post(post_id: int) -> UserPost | None:
    return post_table.get(post_id)

@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(comment: CommentInput):
    post_id = comment.post_id
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    data = comment.model_dump()
    comment_id = len(comment_table)
    new_comment = Comment(id=len(comment_table), **data)
    comment_table[comment_id] = new_comment
    return new_comment

@router.get("/post/{post_id}/comments", response_model=list[Comment])
async def get_comments(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return [comment for comment in comment_table.values() if comment.post_id == post_id]

@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostInput):
    data = post.model_dump()
    post_id = len(post_table)
    new_post = UserPost(id=len(post_table), **data)
    post_table[post_id] = new_post
    return new_post

@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = await get_comments(post_id)
    return UserPostWithComments(post=post, comments=comments)

@router.get("/posts", response_model=list[UserPost])
async def get_posts():
    return list(post_table.values())