from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, Numeric
from datetime import datetime


class Base(DeclarativeBase):
    pass


class VacancyRow(Base):
    __tablename__ = "vacancy"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    salary: Mapped[int | None]
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    applications: Mapped[list["ApplicationRow"]] = relationship(back_populates="vacancy")


class ApplicationRow(Base):
    __tablename__ = "application"

    id: Mapped[int] = mapped_column(primary_key=True)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancy.id", ondelete="CASCADE"))
    status: Mapped[str]

    vacancy: Mapped[VacancyRow] = relationship(back_populates="applications")