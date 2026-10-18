from app.db.base import Base
from app.teacher.teacher_registration.schemas import AccountStatus
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Boolean, Enum as SQLAlchemyEnum
from datetime import datetime, timezone



class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name:Mapped[str] = mapped_column(String(255), nullable=False)
    last_name:Mapped[str] = mapped_column(String(255), nullable=False)
    email:Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verfied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    account_status: Mapped[AccountStatus] = mapped_column(SQLAlchemyEnum(AccountStatus, name="account_status"), default=AccountStatus.PENDING ,nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)


    def __repr__(self):
        return f"<User(id={self.id}, name={f"{self.first_name} {self.last_name}, email={self.email}"} )>"