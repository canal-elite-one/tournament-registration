from marshmallow import (
    Schema,
    fields,
    validate,
    ValidationError,
    pre_load,
    post_load,
    post_dump,
)
from api.shared.api.db import CategoryInDB, PlayerInDB, EntryInDB, is_before_cutoff


class SchemaWithReset(Schema):
    def reset(self, many=False, **kwargs):
        self.many = many
        self.context = dict(kwargs.items())


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

    def reset(self, many=False, include_players=False, present_only=False):
        super().reset(
            many=many,
            include_players=include_players,
            present_only=present_only,
        )

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
        return CategoryInDB(**data)

    # add_entry_count_current_fee & add_players_info are called first (they commute),
    # either on the one serialized object being dumped,
    # or on each serialized object in the list if many=True;
    # then envelop is called on the whole serialized data,
    # doing nothing if many=False and enveloping if many=True
    # cf https://marshmallow.readthedocs.io/en/stable/extending.html#pre-post-processor-invocation-order

    @post_dump(pass_original=True)
    def add_entry_count_current_fee(self, data, original, **kwargs):
        data["entryCount"] = len(original.entries)
        data["presentEntryCount"] = len(original.present_entries())
        data["currentFee"] = original.current_fee()
        return data

    @post_dump(pass_original=True)
    def add_players_info(self, data, original, **kwargs):
        if self.context.get("include_players", False):
            e_schema = EntrySchema()
            e_schema.reset(many=True, include_player=True)
            if self.context.get("present_only", False):
                entries = original.present_entries()
                entries = sorted(entries, key=lambda x: x.registration_time)
                data["entries"] = e_schema.dump(entries)
            elif len(original.entries) <= original.max_players:
                data["absentEntries"] = e_schema.dump(
                    [
                        entry
                        for entry in original.entries
                        if entry.marked_as_present is False
                    ],
                )
                data["entries"] = e_schema.dump(
                    sorted(
                        filter(
                            lambda x: x.marked_as_present is not False,
                            original.entries,
                        ),
                        key=lambda x: x.registration_time,
                    ),
                )
            else:
                entries = original.entries
                data["absentEntries"] = e_schema.dump(
                    [entry for entry in entries if entry.marked_as_present is False],
                )
                entries = sorted(
                    filter(lambda x: x.marked_as_present is not False, entries),
                    key=lambda x: x.registration_time,
                )
                data["overridenEntries"] = e_schema.dump(
                    [
                        entry
                        for entry in entries[original.max_players :]
                        if entry.marked_as_present is True
                    ],
                )
                data["waitingEntries"] = e_schema.dump(
                    [
                        entry
                        for entry in entries[original.max_players :]
                        if entry.marked_as_present is None
                    ],
                )
                unknown_entries = [
                    entry
                    for entry in entries[: original.max_players]
                    if entry.marked_as_present is None
                ]
                data["squeezedEntries"] = (
                    e_schema.dump(
                        unknown_entries[-len(data["overridenEntries"]) :],
                    )
                    if data["overridenEntries"]
                    else []
                )
                normal_present_entries = [
                    entry
                    for entry in entries[: original.max_players]
                    if entry.marked_as_present is True
                ]
                remaining_unknowns = (
                    unknown_entries[: -len(data["overridenEntries"])]
                    if data["overridenEntries"]
                    else unknown_entries
                )
                data["normalEntries"] = e_schema.dump(
                    sorted(
                        normal_present_entries + remaining_unknowns,
                        key=lambda x: x.registration_time,
                    ),
                )

        return data

    @post_dump(pass_many=True)
    def envelop(self, data, many, **kwargs):
        if many:
            return {"categories": data}
        return data


class PlayerSchema(SchemaWithReset):
    licence_no = fields.Str(data_key="licenceNo", required=True, allow_none=False)
    bib_no = fields.Int(data_key="bibNo", dump_only=True)
    first_name = fields.Str(data_key="firstName", required=True, allow_none=False)
    last_name = fields.Str(data_key="lastName", required=True, allow_none=False)
    email = fields.Email(allow_none=False)
    phone = fields.Str(allow_none=False)
    gender = fields.Str(required=True, allow_none=False)
    nb_points = fields.Int(data_key="nbPoints", required=True, allow_none=False)
    club = fields.Str(required=True, allow_none=False)
    total_actual_paid = fields.Int(
        data_key="totalActualPaid",
        dump_only=True,
    )

    def reset(
        self,
        many=False,
        simple_entries=False,
        include_entries=False,
        include_payment_status=False,
    ):
        super().reset(
            many=many,
            simple_entries=simple_entries,
            include_entries=include_entries,
            include_payment_status=include_payment_status,
        )

    @post_load
    def make_object(self, data, **kwargs):
        return PlayerInDB(**data)

    @post_dump(pass_original=True)
    def add_entries_info(self, data, original, **kwargs):
        if self.context.get("simple_entries", False):
            data["registeredEntries"] = ", ".join(
                [
                    entry.category.category_id
                    for entry in sorted(
                        original.entries,
                        key=lambda x: x.category.start_time,
                    )
                ],
            )
        elif self.context.get("include_entries", False):
            e_schema = EntrySchema()
            e_schema.reset(many=True, nest=True, include_rank=True)
            data["registeredEntries"] = e_schema.dump(
                sorted(original.entries, key=lambda x: x.category.start_time),
            )
        return data

    @post_dump(pass_original=True)
    def add_payment_status(self, data, original, **kwargs):
        if self.context.get("include_payment_status", False):
            del data["totalActualPaid"]
            if not is_before_cutoff():
                data["wasRegisteredBeforeCutoff"] = bool(
                    original.entries,
                ) and is_before_cutoff(
                    min(entry.registration_time for entry in original.entries),
                )
                data["paymentStatus"] = original.payment_status()
                data["leftToPay"] = original.left_to_pay()
        return data


class EntrySchema(SchemaWithReset):
    category_id = fields.Str(data_key="categoryId", required=True, allow_none=False)
    licence_no = fields.Str(data_key="licenceNo", dump_only=True)
    color = fields.Str(load_only=True)
    registration_time = fields.DateTime(data_key="registrationTime", dump_only=True)
    marked_as_present = fields.Bool(
        data_key="markedAsPresent",
        allow_none=True,
        required=True,
    )
    marked_as_paid = fields.Bool(
        data_key="markedAsPaid",
        allow_none=False,
        required=True,
    )

    def reset(
        self,
        many=False,
        include_rank=False,
        include_player=False,
        include_category_info=True,
        nest=False,
    ):
        super().reset(
            many=many,
            include_rank=include_rank,
            include_player=include_player,
            include_category_info=include_category_info,
            nest=nest,
        )

    @pre_load(pass_many=True)
    def check_json_field(self, data, many, **kwargs):
        if many and "entries" not in data:
            raise ValidationError(
                "json payload should have 'entries' field.",
                field_name="json",
            )
        return data["entries"]

    @post_load
    def make_entry(self, data, **kwargs):
        return EntryInDB(**data)

    # the two post_dump functions commute.

    @post_dump(pass_original=True)
    def add_entry_fee(self, data, original, **kwargs):
        data["entryFee"] = original.fee()
        return data

    @post_dump(pass_original=True)
    def add_rank(self, data, original, **kwargs):
        if self.context.get("include_rank", False):
            data["rank"] = original.rank()
            return data
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

    @post_dump(pass_original=True)
    def add_category_info(self, data, original, **kwargs):
        if self.context.get("include_category_info", True):
            category = original.category
            data["startTime"] = category.start_time.isoformat()
            data["alternateName"] = category.alternate_name
            data["maxPlayers"] = category.max_players
            data["overbookingPercentage"] = category.overbooking_percentage
        return data

    @post_dump(pass_many=True)
    def nest(self, data, many, **kwargs):
        if many and self.context.get("nest", False):
            result = {}
            for entry in data:
                category_id = entry["categoryId"]
                del entry["categoryId"]
                result[category_id] = entry
            return result
        return data


"""
These schemas are here to validate json payload for api requests.
They only check for presence and correct formatting of field,
as well as static value checking. They do not do dynamic value checking,
i.e. they do not ensure consistency between different columns or table in the db.
"""


class MakePaymentSchema(Schema):
    category_ids = fields.List(
        fields.Str,
        data_key="categoryIds",
        required=True,
        allow_none=False,
    )
    total_actual_paid = fields.Int(
        data_key="totalActualPaid",
        required=True,
        allow_none=False,
        validate=validate.Range(min=0),
    )


class CategoryIdsSchema(Schema):
    category_ids = fields.List(
        fields.Str,
        data_key="categoryIds",
        required=True,
        allow_none=False,
    )


class ContactInfoSchema(Schema):
    phone = fields.Str(required=True, allow_none=False)
    email = fields.Email(required=True, allow_none=False)
