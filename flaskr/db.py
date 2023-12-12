import os
import subprocess
from datetime import datetime

from sqlalchemy import create_engine, Table
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, relationship
from marshmallow import Schema, fields, post_load, post_dump, validate

db_url = os.environ.get("DATABASE_URL")
migration_directory = os.environ.get("MIGRATION_DIR")


def execute_dbmate(command):
    subprocess.run(
        [
            "dbmate",
            "-d",
            migration_directory,
            "--no-dump-schema",
            "--url",
            db_url,
            command,
        ],
        env=os.environ.copy(),
    )


execute_dbmate("up")
engine = create_engine(db_url)

session = Session(engine)


class Base(DeclarativeBase):
    pass


class Category(Base):
    start_time: Mapped[datetime]
    entry_fee: Mapped[int]
    category_id: Mapped[str]

    entries = relationship("Entry", back_populates="category")

    __table__ = Table("categories", Base.metadata, autoload_with=engine)

    def __repr__(self):
        schema = CategorySchema()
        return str(schema.dump(self))


class Player(Base):
    licence_no: Mapped[int]
    bib_no: Mapped[int]
    total_actual_paid: Mapped[int]

    entries = relationship(
        "Entry",
        back_populates="player",
        cascade="all, delete",
        passive_deletes=True,
    )

    __table__ = Table("players", Base.metadata, autoload_with=engine)

    def __repr__(self):
        schema = PlayerSchema()
        return str(schema.dump(self))

    def present_entries(self):
        return filter(lambda x: x.marked_as_present, self.entries)

    def current_required_payment(self):
        return sum(entry.fee() for entry in self.present_entries())


def get_player_not_found_error(licence_no):
    return {
        "error": f"No player with licence number {licence_no} exists in the database.",
    }


class Entry(Base):
    entry_id: Mapped[int]
    marked_as_present: Mapped[bool]
    category_id: Mapped[str]
    licence_no: Mapped[int]
    marked_as_paid: Mapped[bool]

    player = relationship("Player", back_populates="entries")
    category = relationship("Category", back_populates="entries")

    __table__ = Table("entries", Base.metadata, autoload_with=engine)

    def __repr__(self):
        schema = EntrySchema()
        return str(schema.dump(self))

    def fee(self):
        return self.category.entry_fee


class CategorySchema(Schema):
    category_id = fields.Str(data_key="categoryId", validate=validate.Length(equal=1))
    alternate_name = fields.Str(
        data_key="alternateName",
        validate=validate.Length(max=64),
    )
    color = fields.Str(validate=validate.Length(equal=7))
    min_points = fields.Int(data_key="minPoints")
    max_points = fields.Int(data_key="maxPoints")
    start_time = fields.DateTime(data_key="startTime", allow_none=False, required=True)
    women_only = fields.Bool(data_key="womenOnly")
    entry_fee = fields.Int(data_key="entryFee", allow_none=False, required=True)
    reward_first = fields.Int(data_key="rewardFirst", allow_none=False, required=True)
    reward_second = fields.Int(data_key="rewardSecond", allow_none=False, required=True)
    reward_semi = fields.Int(data_key="rewardSemi", allow_none=False, required=True)
    reward_quarter = fields.Int(data_key="rewardQuarter")
    max_players = fields.Int(data_key="maxPlayers", allow_none=False, required=True)
    overbooking_percentage = fields.Int(data_key="overbookingPercentage")

    @post_load
    def make_field(self, data, **kwargs):
        return Category(**data)

    # add_entry_count is called first, either on the one serialized object being dumped,
    # or on each serialized object in the list if many=True;
    # then envelop is called on the whole serialized data,
    # doing nothing if many=False and enveloping if many=True
    # cf https://marshmallow.readthedocs.io/en/stable/extending.html#pre-post-processor-invocation-order

    @post_dump(pass_original=True)
    def add_entry_count(self, data, original, **kwargs):
        data["entryCount"] = len(original.entries)
        return data

    @post_dump(pass_many=True)
    def envelop(self, data, many, **kwargs):
        if many:
            return {"categories": data}
        return data


class PlayerSchema(Schema):
    # TODO: use nested fields for licence_no & bib_no, maybe change to player & category
    licence_no = fields.Int(data_key="licenceNo")
    bib_no = fields.Int(data_key="bibNo", validate=validate.Equal(None))
    first_name = fields.Str(data_key="firstName", required=True)
    last_name = fields.Str(data_key="lastName", required=True)
    email = fields.Email(required=True)
    phone = fields.Str(required=True)
    gender = fields.Str(required=True)
    nb_points = fields.Int(data_key="nbPoints", required=True)
    club = fields.Str(required=True)
    total_actual_paid = fields.Int(data_key="totalActualPaid")

    @post_load
    def make_field(self, data, **kwargs):
        return Player(**data)

    @post_dump(pass_original=True)
    def add_entries_info(self, data, original, **kwargs):
        if self.context.get("include_entries", False):
            data["registeredEntries"] = EntrySchema(many=True).dump(
                sorted(original.entries, key=lambda x: x.category.start_time),
            )
        return data


class EntrySchema(Schema):
    category_id = fields.Str(data_key="categoryId")
    licence_no = fields.Int(data_key="licenceNo")
    color = fields.Str(load_only=True)
    registration_time = fields.DateTime(data_key="registrationTime")
    marked_as_paid = fields.Bool(data_key="markedAsPaid")
    marked_as_present = fields.Bool(data_key="markedAsPresent")

    @post_load
    def make_field(self, data, **kwargs):
        return Entry(**data)
