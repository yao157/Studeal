from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import String, Numeric, DateTime, ForeignKey, BigInteger, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.database.models.base import Base

class Post(Base):
    """
    Модель завдання/оголошення.
    Зберігає інформацію про завдання, які створюють замовники.
    """
    __tablename__ = 'posts'

    # 1. Ідентифікація
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # 2. Основна інформація
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(5000))  # Може бути довгий опис
    budget: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    category: Mapped[str] = mapped_column(String(50))  # Наприклад: "design", "programming", "writing"
    
    # 3. Тип та статус
    post_type: Mapped[str] = mapped_column(String(20), default="public")  # "public" або "private"
    status: Mapped[str] = mapped_column(
        String(20), 
        default="draft",
    )
    
    # 4. Зв'язки з користувачами
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    executor_id: Mapped[int | None] = mapped_column(
        BigInteger, 
        ForeignKey('users.telegram_id'), 
        nullable=True
    )
    
    # 5. Telegram інтеграція
    channel_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    
    # 6. Технічні поля
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now(), 
        server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # 7. Relationships
    author = relationship("User", foreign_keys=[author_id], back_populates="posts_as_author")
    executor = relationship("User", foreign_keys=[executor_id], back_populates="posts_as_executor")

    # 8. Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'moderation', 'published', 'working', 'completed', 'archived', 'dispute', 'cancelled')",
            name='check_post_status'
        ),
    )

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', status={self.status})>"

