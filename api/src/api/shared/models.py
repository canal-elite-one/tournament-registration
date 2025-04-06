from __future__ import annotations

from typing import Self


from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from api.shared.api.db import EntryInDB


def snake_case_to_camel_case(snake: str) -> str:
    return "".join(x.capitalize() for x in snake.split("_"))


class AliasedBase(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda field_name: snake_case_to_camel_case(field_name),
        populate_by_name=True,
        from_attributes=True,
    )


class Category(AliasedBase):
    category_id: str = Field(min_length=1, max_length=1)
    alternate_name: str = Field(max_length=64)
    color: str = Field(min_length=7, max_length=7)
    min_points: int
    max_points: int
    start_time: datetime
    women_only: bool
    base_registration_fee: int
    late_registration_fee: int
    reward_first: int
    reward_second: int
    reward_semi: int
    reward_quarter: int | None
    max_players: int
    overbooking_percentage: int | None


class Gender(StrEnum):
    M = "M"
    F = "F"


class FfttPlayer(AliasedBase):
    licence_no: str
    first_name: str
    last_name: str
    club: str
    gender: Gender
    nb_points: int


class ContactInfo(AliasedBase):
    email: str
    phone: str | None


class Player(FfttPlayer):
    bib_no: int | None
    email: str
    phone: str | None
    total_actual_paid: int | None


class Entry(AliasedBase):
    category_id: str = Field(min_length=1, max_length=1)
    licence_no: str
    color: str = Field(min_length=7, max_length=7)
    registration_time: datetime | None
    marked_as_present: bool | None
    marked_as_paid: bool


class EntryWithPlayer(Player, Entry):
    @classmethod
    def from_entry_in_db(cls, entry_in_db: EntryInDB) -> Self:
        player_in_db = entry_in_db.player
        temp_dict = Entry.model_validate(entry_in_db).model_dump()
        del temp_dict["licence_no"]
        return cls(**temp_dict, **Player.model_validate(player_in_db).model_dump())
