import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    checks = relationship("VehicleCheck", back_populates="user")


class VehicleCheck(Base):
    __tablename__ = "vehicle_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    registration = Column(String(20), nullable=False)
    listing_url = Column(Text)
    listing_price = Column(Integer)

    make = Column(String(100))
    model = Column(String(100))
    year = Column(Integer)

    mot_data = Column(JSONB)
    market_data = Column(JSONB)
    analysis_result = Column(JSONB)

    product = Column(String(20), default="car", nullable=False)
    status = Column(String(50), default="pending")
    tier = Column(String(20))
    price_paid = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="checks")
    payment = relationship("Payment", back_populates="check", uselist=False)

    __table_args__ = (
        Index("idx_vehicle_checks_registration", "registration"),
        Index("idx_vehicle_checks_status", "status"),
        Index("idx_vehicle_checks_product", "product"),
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    check_id = Column(UUID(as_uuid=True), ForeignKey("vehicle_checks.id", ondelete="CASCADE"))
    stripe_payment_intent_id = Column(String(255), unique=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), default="gbp")
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    check = relationship("VehicleCheck", back_populates="payment")
