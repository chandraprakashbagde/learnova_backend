from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum as SqlAlchemyEnum, Integer, Boolean, DateTime, ForeignKey
from app.auth.schemas import Role
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) 
    name: Mapped[str] = mapped_column(String(255), nullable=False) 
    email: Mapped[str] = mapped_column(String(255), nullable=False) 
    phone: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped["Role"] = mapped_column(SqlAlchemyEnum(Role, name="role"), nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    refresh_tokens:Mapped[list["RefreshToken"]] = relationship("RefreshToken", back_populates="user")

    def __repr__(self):
        return f"""<User(
            id={self.id}
            name={self.name}
            email={self.email}
            phone={self.phone}
            password={self.password}
            role={self.role}
            email_verified={self.email_verified}
            email_verified_at={self.email_verified_at}
            created_at={self.created_at}
        )>"""


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"RefreshToken(id={self.id}, user_id={self.user_id}, token={self.token}, expires_at={self.expires_at}, revoked={self.revoked})"
    