import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.infrastructure.models  # noqa: F401
from app.infrastructure.db.base import Base
from app.infrastructure.db.seeds.catalogos import seed_catalogos


@pytest.fixture
def sesion():
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(motor)
    Sesion = sessionmaker(bind=motor, autoflush=False)
    with Sesion() as sesion:
        seed_catalogos(sesion)
        sesion.flush()
        yield sesion
    Base.metadata.drop_all(motor)
    motor.dispose()
