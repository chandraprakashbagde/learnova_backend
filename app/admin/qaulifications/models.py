from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime
from datetime import datetime, timezone
from app.teacher.profile.models import teachers_qualifications

class Qualifications(Base):
    __tablename__ = "qualifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    teachers_profile:Mapped[list["TeacherProfile"]] = relationship(secondary=teachers_qualifications, back_populates="qualifications")

    def __repr__(self):
        return f"<Qualifications(id={self.id}, name={self.name}, created_at={self.created_at})>"
    
    