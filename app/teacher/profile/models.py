from app.db.base import Base
from app.teacher.profile.schemas import VerificationStatus
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Boolean, Enum as SQLAlchemyEnum, ForeignKey, Text, Table, Column
from datetime import datetime, timezone
from app.auth.models import User


teachers_subject = Table(
    "teachers_subjects",
    Base.metadata,
    Column("subject_id", ForeignKey("subjects.id"), primary_key=True),
    Column("teacher_id", ForeignKey("teachers_profile.id"), primary_key=True)
)

class TeacherProfile(Base):
    __tablename__ = "teachers_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    exprience: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    verification_status: Mapped[VerificationStatus] = mapped_column(SQLAlchemyEnum(VerificationStatus), default=VerificationStatus.ACCOUNT_CREATED)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda:datetime.now(timezone.utc), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="teachers_profile")

    teachers_subjects: Mapped[list["Subject"]] = relationship(secondary=teachers_subject, back_populates="teachers_profile")

    def __repr__(self):
        return f"<TeacherProfile(id={self.id}, name={f"{self.first_name} {self.last_name}, email={self.email}"} )>"