from datetime import date, datetime
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, generics
from sqlalchemy import String, Date, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    surname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50))
    number: Mapped[str] = mapped_column(String(20))
    birthday: Mapped[date] = mapped_column(Date())
    description: Mapped[str] = mapped_column(String(250))
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now(),
                                                 nullable=True)
    user_id: Mapped[generics.GUID] = mapped_column(generics.GUID(), ForeignKey('user.id'), nullable=True)
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")


class User(SQLAlchemyBaseUserTableUUID, Base):
    username: Mapped[str] = mapped_column(String(50))
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
