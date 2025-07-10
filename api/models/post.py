from pydantic import BaseModel

class UserPostInput(BaseModel):
    body: str

class UserPost(UserPostInput):
    id: int
    
class CommentInput(BaseModel):
    body: str
    post_id: int

class Comment(CommentInput):
    id: int

class UserPostWithComments(UserPost):
    comments: list[Comment]
    post: UserPost