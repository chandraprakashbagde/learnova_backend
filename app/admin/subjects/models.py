from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Table, Column, Boolean
from app.teacher.profile.models import teachers_subject



class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    teachers_profile: Mapped[list["TeacherProfile"]] = relationship(secondary=teachers_subject, back_populates="subjects")

    
    def __repr__(self):
        return f"<Subject(id={self.id}, name={self.name})>"

