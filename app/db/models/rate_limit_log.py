from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, Integer, String, func

from app.db.base import Base

class RateLimitLog(Base):

    __tablename__ = "rate_limit_log"


    id: Mapped[int] = mapped_column(primary_key=True)

    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


''' TODO:
add index on merchant_id
add index on created_at
composite index on (merchant_id, endpoint, created_at)

------------------- WHY? ---------------------
That composite index is especially useful because your main query pattern is:
this merchant
this endpoint
recent time window
'''