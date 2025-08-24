from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, create_engine
import databases
from api.config import config

metadata = MetaData()

post_table = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("body", String, nullable=False),
)

comment_table = Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("body", String, nullable=False),
    Column("post_id", Integer, ForeignKey("posts.id"), nullable=False),
)

user_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
)

engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})

metadata.create_all(engine)

database = databases.Database(config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK)