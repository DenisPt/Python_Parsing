from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime

Base = declarative_base()


class IdMixin:
    id = Column(Integer, autoincrement=True, primary_key=True)


class UrlMixin:
    url = Column(String, unique=True, nullable=False)


class NameMixin:
    name = Column(String, nullable=False)


tag_post = Table(
    "tag_post",
    Base.metadata,
    Column('post_id', Integer, ForeignKey("post.id")),
    Column('tag_id', Integer, ForeignKey("tag.id")),
)


class Post(IdMixin, UrlMixin, Base):
    __tablename__ = "post"
    title = Column(String, nullable=False)
    picture_url = Column(String)
    author_id = Column(Integer, ForeignKey("author.id"))
    date_pub = Column(DateTime, nullable=False)
    author = relationship("Author")
    tags = relationship("Tag", secondary=tag_post)
    comment = relationship("Comment")


class Author(IdMixin, UrlMixin, NameMixin, Base):
    __tablename__ = "author"
    posts = relationship("Post")
    comments = relationship("Comment")


class Tag(IdMixin, UrlMixin, NameMixin, Base):
    __tablename__ = "tag"
    posts = relationship("Post", secondary=tag_post)


class Comment(IdMixin, Base):
    __tablename__ = "comment"
    body = Column(String, nullable=False)
    writer_id = Column(Integer, ForeignKey("author.id"))
    writer = relationship("Author")
    post_id = Column(Integer, ForeignKey("post.id"))
    post = relationship("Post")

