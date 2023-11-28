import os
import subprocess
from sqlalchemy import create_engine, Table
from sqlalchemy.orm import DeclarativeBase, Session
from marshmallow import Schema, fields, post_load

db_url = os.environ.get("DATABASE_URL", None) or "postgresql+psycopg2://postgres:postgres@localhost:5432/tournois"
subprocess.run(["dbmate", "-d", os.environ.get("MIGRATION_DIR"), "--no-dump-schema", "--url", db_url, "up"])
engine = create_engine(db_url)

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
                 "entry_fee", "reward_first", "reward_second", "reward_semi", "reward_quarter",
                 "max_players", "overbooking_percentage"]}


class Players(Base):
    __table__ = Table("players", Base.metadata, autoload_with=engine)


class Entries(Base):
    __table__ = Table("entries", Base.metadata, autoload_with=engine)


class CategorySchema(Schema):
    category_id = fields.Str(data_key='categoryID')
    color = fields.Str()
    min_points = fields.Int(data_key='minPoints')
    max_points = fields.Int(data_key='maxPoints')
    start_time = fields.DateTime(data_key='startTime', allow_none=False, required=True)
    women_only = fields.Bool(data_key='womenOnly')
    entry_fee = fields.Int(data_key='entryFee')
    reward_first = fields.Int(data_key='rewardFirst')
    reward_second = fields.Int(data_key='rewardSecond')
    reward_semi = fields.Int(data_key='rewardSemi')
    reward_quarter = fields.Int(data_key='rewardQuarter')
    max_players = fields.Int(data_key='maxPlayers')
    overbooking_percentage = fields.Int(data_key='overbookingPercentage')

    @post_load
    def make_field(self, data, **kwargs):
        return Categories(**data)


class PlayerSchema(Schema):
    # TODO: use nested fields for licence_no & bib_no, maybe change to player & category?
    licence_no = fields.Int(data_key='licenceNo')
    bib_no = fields.Int(data_key='bibNo')
    first_name = fields.Str(data_key='firstName', required=True)
    last_name = fields.Str(data_key='lastName', required=True)
    email = fields.Email(required=True)
    phone = fields.Str(required=True)
    gender = fields.Str()
    nb_points = fields.Int(data_key='nbPoints', required=True)
    club = fields.Str(required=True)

    @post_load
    def make_field(self, data, **kwargs):
        return Players(**data)


class EntrySchema(Schema):
    entry_id = fields.Int(data_key='entryID')
    category_id = fields.Str(data_key='categoryID')
    licence_no = fields.Int(data_key='licenceNo')
    color = fields.Str()
    registration_time = fields.DateTime(data_key='registrationTime')
    paid = fields.Bool()
    showed_up = fields.Bool(data_key='showedUp')

    @post_load
    def make_field(self, data, **kwargs):
        return Entries(**data)
