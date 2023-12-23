import os
import subprocess
from datetime import datetime
from functools import cached_property

from sqlalchemy import create_engine, Table, select, func
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, relationship
from marshmallow import (
    Schema,
    fields,
    pre_load,
    post_load,
    post_dump,
    validate,
    ValidationError,
)

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


class AppWideInfo:
    @cached_property
    def registration_cutoff(self):
        tournament_start = session.scalar(select(func.min(Category.start_time)))
        if tournament_start is None:
            return None
        return tournament_start.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )


app_info = AppWideInfo()


class Base(DeclarativeBase):
    pass


class Category(Base):
    start_time: Mapped[datetime]
    base_registration_fee: Mapped[int]
    category_id: Mapped[str]
    late_registration_fee: Mapped[int]

    entries = relationship("Entry", back_populates="category")

    __table__ = Table("categories", Base.metadata, autoload_with=engine)

    def __repr__(self):
        schema = CategorySchema()
        return str(schema.dump(self))

    def present_entries(self):
        return filter(lambda x: x.marked_as_present, self.entries)

    def current_fee(self):
        result = self.base_registration_fee
        if datetime.now() > app_info.registration_cutoff:
            result += self.late_registration_fee
        return result


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
    registration_time: Mapped[datetime]

    player = relationship("Player", back_populates="entries")
    category = relationship("Category", back_populates="entries")

    __table__ = Table("entries", Base.metadata, autoload_with=engine)

    def __repr__(self):
        schema = EntrySchema()
        return str(schema.dump(self))

    def fee(self):
        result = self.category.base_registration_fee
        if self.registration_time > app_info.registration_cutoff:
            result += self.category.late_registration_fee
        return result


class SchemaWithReset(Schema):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def reset(self, many=False):
        self.many = many
        self.context = {}


class CategorySchema(SchemaWithReset):
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
    base_registration_fee = fields.Int(
        data_key="baseRegistrationFee",
        allow_none=False,
        required=True,
    )
    late_registration_fee = fields.Int(
        data_key="lateRegistrationFee",
        allow_none=False,
        required=True,
    )
    reward_first = fields.Int(data_key="rewardFirst", allow_none=False, required=True)
    reward_second = fields.Int(data_key="rewardSecond", allow_none=False, required=True)
    reward_semi = fields.Int(data_key="rewardSemi", allow_none=False, required=True)
    reward_quarter = fields.Int(data_key="rewardQuarter")
    max_players = fields.Int(data_key="maxPlayers", allow_none=False, required=True)
    overbooking_percentage = fields.Int(data_key="overbookingPercentage")

    @pre_load(pass_many=True)
    def check_json_field(self, data, many, **kwargs):
        if many and "categories" not in data:
            raise ValidationError(
                "json payload should have 'categories' field.",
                field_name="json",
            )
        return data["categories"]

    # as below, check_duplicates with pass_many=True is called
    # before make_object with pass_many=False

    @post_load(pass_many=True)
    def check_duplicates(self, data, many, **kwargs):
        if len({cat_dict["category_id"] for cat_dict in data}) < len(data):
            raise ValidationError(
                "Different categories cannot have the same id",
                field_name="category_ids",
            )
        return data

    @post_load
    def make_object(self, data, **kwargs):
        return Category(**data)

    # add_entry_count_current_fee & add_players_info are called first (they commute),
    # either on the one serialized object being dumped,
    # or on each serialized object in the list if many=True;
    # then envelop is called on the whole serialized data,
    # doing nothing if many=False and enveloping if many=True
    # cf https://marshmallow.readthedocs.io/en/stable/extending.html#pre-post-processor-invocation-order

    @post_dump(pass_original=True)
    def add_entry_count_current_fee(self, data, original, **kwargs):
        data["entryCount"] = len(original.entries)
        data["currentFee"] = original.current_fee()
        return data

    @post_dump(pass_original=True)
    def add_players_info(self, data, original, **kwargs):
        if self.context.get("include_players", False):
            if self.context.get("present_only", False):
                entries = original.present_entries()
            else:
                entries = original.entries
            entries = sorted(entries, key=lambda x: x.registration_time)
            e_schema = EntrySchema(many=True)
            e_schema.context["include_player"] = True
            data["entries"] = e_schema.dump(entries)
        return data

    @post_dump(pass_many=True)
    def envelop(self, data, many, **kwargs):
        if many:
            return {"categories": data}
        return data


class PlayerSchema(SchemaWithReset):
    licence_no = fields.Int(data_key="licenceNo", required=True, allow_none=False)
    bib_no = fields.Int(data_key="bibNo", dump_only=True)
    first_name = fields.Str(data_key="firstName", required=True, allow_none=False)
    last_name = fields.Str(data_key="lastName", required=True, allow_none=False)
    email = fields.Email(required=True, allow_none=False)
    phone = fields.Str(required=True, allow_none=False)
    gender = fields.Str(required=True, allow_none=False)
    nb_points = fields.Int(data_key="nbPoints", required=True, allow_none=False)
    club = fields.Str(required=True, allow_none=False)
    total_actual_paid = fields.Int(
        data_key="totalActualPaid",
        dump_only=True,
    )

    @post_load
    def make_object(self, data, **kwargs):
        return Player(**data)

    @post_dump(pass_original=True)
    def add_entries_info(self, data, original, **kwargs):
        if self.context.get("include_entries", False):
            data["registeredEntries"] = EntrySchema(many=True).dump(
                sorted(original.entries, key=lambda x: x.category.start_time),
            )
            data["currentRequiredPayment"] = original.current_required_payment()
        return data


class EntrySchema(SchemaWithReset):
    category_id = fields.Str(data_key="categoryId")
    licence_no = fields.Int(data_key="licenceNo")
    color = fields.Str(load_only=True)
    registration_time = fields.DateTime(data_key="registrationTime")
    marked_as_paid = fields.Bool(data_key="markedAsPaid")
    marked_as_present = fields.Bool(data_key="markedAsPresent")

    @post_load
    def make_field(self, data, **kwargs):
        return Entry(**data)

    # the two post_dump functions commute.

    @post_dump(pass_original=True)
    def add_entry_fee(self, data, original, **kwargs):
        data["entryFee"] = original.fee()
        return data

    @post_dump(pass_original=True)
    def add_player_info(self, data, original, **kwargs):
        if self.context.get("include_player", False):
            player = original.player
            data["firstName"] = player.first_name
            data["lastName"] = player.last_name
            data["bibNo"] = player.bib_no
            data["nbPoints"] = player.nb_points
            data["club"] = player.club
            del data["categoryId"]
        return data
