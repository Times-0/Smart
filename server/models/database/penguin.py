import orm
from server.core.config import DATABASE
from server.models.database import metadata


class Penguin(orm.Model):
    __database__ = DATABASE
    __metadata__ = metadata
    __tablename__ = "penguins"

    id = orm.Integer(primary_key=True)
    nickname = orm.String(max_length=30, allow_null=False)
    swid = orm.String(max_length=40, allow_null=False, unique=True)
