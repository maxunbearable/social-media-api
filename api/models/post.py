from pydantic import BaseModel, ConfigDict

class UserPostInput(BaseModel):
    body: str

class UserPost(UserPostInput):
    model_config = ConfigDict(from_attributes=True)
    id: int

class CommentInput(BaseModel):
    body: str
    post_id: int

class Comment(CommentInput):
    model_config = ConfigDict(from_attributes=True)
    id: int

class UserPostWithComments(BaseModel):
    post: UserPost
    comments: list[Comment]