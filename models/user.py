from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from sqlalchemy import Column, Integer, ForeignKey, text


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String, nullable=False)


    role_id = Column(
        Integer,
        ForeignKey("roles.id"),
        nullable=False,
        server_default=text("3")
    )

    department_id = Column(
        Integer,
        ForeignKey("departments.id"),
        nullable=False,
        server_default=text("3")
    )

    is_active = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    role = relationship("Role")
    department = relationship("Department")
    records = relationship(
    "Record",
    back_populates="user",
    foreign_keys="Record.created_by"   
)