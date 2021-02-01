from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models


class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.drop_all(engine)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def get_or_create(self, session, model, **data):
        try:
            db_data = session.query(model).filter(model.url == data["url"]).first()
        except AttributeError:
            db_data = 0
        except KeyError:
            db_data = model(**data)
        if not db_data:
            db_data = model(**data)
        return db_data

    def create_post(self, data):
        session = self.maker()
        author = self.get_or_create(session, models.Author, **data["author"])
        post = self.get_or_create(session, models.Post, **data["post_data"], author=author)
        tags = map(
            lambda tag_data: self.get_or_create(session, models.Tag, **tag_data), data["tags"]
        )
        post.tags.extend(tags)
        if data["comment"]:
            for comment in data["comment"]:
                writer = {"name": comment.pop("writer_name"), "url": comment.pop("writer_url")}
                writer = self.get_or_create(session, models.Author, **writer)
                comment = self.get_or_create(session, models.Comment, **comment, post=post, writer=writer)
                session.add(comment)
        session.add(post)
        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()
