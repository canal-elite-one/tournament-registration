import os
import subprocess
from datetime import datetime

from sqlalchemy import create_engine, Table, select, func, not_, delete
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, relationship

import apis.shared.config as cfg


def execute_dbmate(command):
    subprocess.run(
        [
            "dbmate",
            "-d",
            cfg.MIGRATION_DIR,
            "--no-dump-schema",
            "--url",
            cfg.DATABASE_URL,
            command,
        ],
        env=os.environ.copy(),
    )


engine = create_engine(cfg.DATABASE_URL)

Session = sessionmaker(engine)


def is_before_cutoff(dt=None):
    if dt is None:
        dt = datetime.now()
    return dt < cfg.TOURNAMENT_REGISTRATION_CUTOFF


def is_before_start(dt=None):
    if dt is None:
        dt = datetime.now()
    return dt < cfg.TOURNAMENT_REGISTRATION_START


class Base(DeclarativeBase):
    pass


class CategoryInDB(Base):
    women_only: Mapped[bool]
    start_time: Mapped[datetime]
    base_registration_fee: Mapped[int]
    category_id: Mapped[str]
    late_registration_fee: Mapped[int]
    max_players: Mapped[int]
    color: Mapped[str]

    entries = relationship("EntryInDB", back_populates="category")

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


class PlayerInDB(Base):
    licence_no: Mapped[str]
    bib_no: Mapped[int]
    total_actual_paid: Mapped[int]
    gender: Mapped[str]
    nb_points: Mapped[int]
    first_name: Mapped[str]
    email: Mapped[str]

    entries = relationship(
        "EntryInDB",
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


class EntryInDB(Base):
    entry_id: Mapped[int]
    marked_as_present: Mapped[bool]
    category_id: Mapped[str]
    licence_no: Mapped[str]
    color: Mapped[str]
    marked_as_paid: Mapped[bool]
    registration_time: Mapped[datetime]

    player = relationship("PlayerInDB", back_populates="entries")
    category = relationship("CategoryInDB", back_populates="entries")

    __table__ = Table("entries", Base.metadata, autoload_with=engine)

    def fee(self):
        result = self.category.base_registration_fee
        if not is_before_cutoff(self.player.first_entry_registration_time()):
            result += self.category.late_registration_fee
        return result

    def rank(self):
        with Session() as session:
            return (
                session.scalar(
                    select(func.count())
                    .select_from(EntryInDB)
                    .where(
                        EntryInDB.category_id == self.category_id,
                        EntryInDB.registration_time < self.registration_time,
                        not_(EntryInDB.marked_as_present.is_(False)),
                    ),
                )
                + 1
            )

    def is_in_waiting_list(self):
        return self.rank() >= self.category.max_players * (
            1 + self.category.overbooking_percentage / 100
        )

    def __repr__(self):
        return (
            f"<Entry licence_no:{self.licence_no}, category_id:{self.category_id}, "
            f"present:{self.marked_as_present}, paid:{self.marked_as_paid}>"
        )


def empty_db():
    with Session() as session:
        session.execute(delete(EntryInDB))
        session.execute(delete(PlayerInDB))
        session.execute(delete(CategoryInDB))
        session.commit()
