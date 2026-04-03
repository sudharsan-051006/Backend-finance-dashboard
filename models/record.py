from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from sqlalchemy import Column, String

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)

    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(200))

    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(String(20), default="pending")

    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(TIMESTAMP, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    category = relationship("Category")
    custom_category = Column(String(100), nullable=True)
    creator = relationship("User", foreign_keys=[created_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by]) 

    type = Column(String(10), nullable=False)  # income / expense

    user = relationship(
    "User",
    back_populates="records",
    foreign_keys=[created_by]   
)