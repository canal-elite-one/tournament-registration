import os
import subprocess
from datetime import datetime

from flask import current_app
from sqlalchemy import create_engine, Table, select, func, not_
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, relationship

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

Session = sessionmaker(engine)


def is_before_cutoff():
    return datetime.now() < current_app.config["TOURNAMENT_REGISTRATION_CUTOFF"]


class Base(DeclarativeBase):
    pass


class Category(Base):
    start_time: Mapped[datetime]
    base_registration_fee: Mapped[int]
    category_id: Mapped[str]
    late_registration_fee: Mapped[int]

    entries = relationship("Entry", back_populates="category")

    __table__ = Table("categories", Base.metadata, autoload_with=engine)

    def present_entries(self):
        return filter(lambda x: x.marked_as_present, self.entries)

    def current_fee(self):
        result = self.base_registration_fee
        if not is_before_cutoff():
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

    def paid_entries(self):
        return filter(lambda x: x.marked_as_paid, self.entries)

    def present_entries(self):
        return filter(lambda x: x.marked_as_present, self.entries)

    def _fees_total_registered(self):
        return sum(entry.fee() for entry in self.entries)

    def fees_total_present(self):
        return sum(entry.fee() for entry in self.present_entries())

    def _fees_total_paid(self):
        return sum(entry.fee() for entry in self.paid_entries())

    def payment_status(self):
        return {
            "totalActualPaid": self.total_actual_paid,
            "totalRegistered": self._fees_total_registered(),
            "totalPresent": self.fees_total_present(),
            "totalPaid": self._fees_total_paid(),
        }

    def left_to_pay(self):
        return self.fees_total_present() - self.total_actual_paid


def get_player_not_found_error(licence_no):
    return {
        "PLAYER_NOT_FOUND_ERROR": f"No player with licence "
        f"number {licence_no} exists in the database.",
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

    def fee(self):
        result = self.category.base_registration_fee
        if (
            self.registration_time
            > current_app.config["TOURNAMENT_REGISTRATION_CUTOFF"]
        ):
            result += self.category.late_registration_fee
        return result

    def rank(self):
        with Session() as session:
            return session.scalar(
                select(func.count())
                .select_from(Entry)
                .where(
                    Entry.category_id == self.category_id,
                    Entry.registration_time < self.registration_time,
                    not_(Entry.marked_as_present.is_(False)),
                ),
            )
