import pytest
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

from src.domain.plan import Plan
from src.domain.value_objects import MonetaryValue
from src.infra.db import SQLModelPlanRepository


engine = create_engine("sqlite:///:memory:")

@pytest.fixture
def session():
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_save_plan_to_db(session):
    repo = SQLModelPlanRepository(session)
    plan = Plan(name="Standard", price=MonetaryValue(amount=10, currency="BRL"))
    repo.save(plan)

    saved_plan = repo.find_by_id(plan.id)
    assert saved_plan
