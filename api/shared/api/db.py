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


engine = create_engine(db_url)

Session = sessionmaker(engine)


def is_before_cutoff(dt=None):
    if dt is None:
        dt = datetime.now()
    return dt < current_app.config["TOURNAMENT_REGISTRATION_CUTOFF"]


def is_before_start(dt=None):
    if dt is None:
        dt = datetime.now()
    return dt < current_app.config["TOURNAMENT_REGISTRATION_START"]


class Base(DeclarativeBase):
    pass


class Category(Base):
    women_only: Mapped[bool]
    start_time: Mapped[datetime]
    base_registration_fee: Mapped[int]
    category_id: Mapped[str]
    late_registration_fee: Mapped[int]
    max_players: Mapped[int]

    entries = relationship("Entry", back_populates="category")

    __table__ = Table("categories", Base.metadata, autoload_with=engine)

    def present_entries(self):
        return [entry for entry in self.entries if entry.marked_as_present]

    def current_fee(self):
        result = self.base_registration_fee
        if not is_before_cutoff():
            result += self.late_registration_fee
        return result

    def __repr__(self):
        return f"<Category {self.category_id}>"


class Player(Base):
    licence_no: Mapped[str]
    bib_no: Mapped[int]
    total_actual_paid: Mapped[int]
    gender: Mapped[str]
    nb_points: Mapped[int]

    entries = relationship(
        "Entry",
        back_populates="player",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
    )

    __table__ = Table("players", Base.metadata, autoload_with=engine)

    def __repr__(self):
        return f"<Player {self.licence_no}>"

    def respects_gender_points_constraints(self, category):
        return (not category.women_only or self.gender == "F") and (
            category.min_points <= self.nb_points <= category.max_points
        )

    def paid_entries(self):
        return [entry for entry in self.entries if entry.marked_as_paid]

    def present_entries(self):
        return [entry for entry in self.entries if entry.marked_as_present]

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

    def first_entry_registration_time(self):
        return min(entry.registration_time for entry in self.entries)


class Entry(Base):
    entry_id: Mapped[int]
    marked_as_present: Mapped[bool]
    category_id: Mapped[str]
    licence_no: Mapped[str]
    marked_as_paid: Mapped[bool]
    registration_time: Mapped[datetime]

    player = relationship("Player", back_populates="entries")
    category = relationship("Category", back_populates="entries")

    __table__ = Table("entries", Base.metadata, autoload_with=engine)

    def fee(self):
        result = self.category.base_registration_fee
        if not is_before_cutoff(self.player.first_entry_registration_time()):
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

    def __repr__(self):
        return (
            f"<Entry licence_no:{self.licence_no}, category_id:{self.category_id}, "
            f"present:{self.marked_as_present}, paid:{self.marked_as_paid}>"
        )
