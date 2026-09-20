import datetime
import uuid

from sqlalchemy.orm import Mapped, mapped_column

from swellbeing_api.database import db


class User(db.Model):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)

    def to_dict(self):
        return {"id": str(self.id)}


class WaterIntake(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(db.ForeignKey("user.id"), nullable=False)
    volume: Mapped[float] = mapped_column(db.Float, nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.now(tz=datetime.UTC),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": str(self.user_id),
            "volume": self.volume,
            "timestamp": self.timestamp.isoformat(),
        }
