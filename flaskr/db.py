from sqlalchemy import create_engine, Table
from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/tournois")

session = Session(engine)


class Base(DeclarativeBase):
    pass


class Categories(Base):
    __table__ = Table("categories", Base.metadata, autoload_with=engine)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {att: getattr(self, att) for att in
                ["category_id", "color", "min_points", "max_points", "start_time", "women_only",
                 "inscription_fee", "reward_first", "reward_second", "reward_semi", "reward_quarter",
                 "max_players", "overbooking_percentage"]}


class Players(Base):
    __table__ = Table("players", Base.metadata, autoload_with=engine)


class Inscriptions(Base):
    __table__ = Table("inscriptions", Base.metadata, autoload_with=engine)

