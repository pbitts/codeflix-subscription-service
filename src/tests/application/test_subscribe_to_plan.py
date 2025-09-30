from decimal import Decimal
from unittest.mock import create_autospec

import pytest

from src.application.subscribe_to_plan import (
    SubscribeToPlanUseCase,
    SubscribeToPlanInput,
)
from src.domain.plan import Plan
from src.domain.user_account import UserAccount, Address
from src.domain.value_objects import MonetaryValue
from src.infra.payment.payment_gateway import PaymentGateway, Payment
from src.tests.fixtures.infra.repositories import (
    InMemoryPlanRepository,
    InMemoryUserAccountRepository,
    InMemorySubscriptionRepository,
)


@pytest.fixture
def user_account():
    return UserAccount(
        iam_user_id="123456789012",
        name="test-user",
        email="test@user.com",
        billing_address=Address(
            street="123 Main St",
            city="Anytown",
            state="NY",
            zip_code="12345",
            country="BRL",
        ),
    )


@pytest.fixture
def basic_plan():
    return Plan(
        name="Basic", price=MonetaryValue(amount=Decimal("49.90"), currency="BRL")
    )


class TestSubscribeToPlanUseCase:
    def test_when_payment_succeeds_then_create_subscription(
        self,
        user_account,
        basic_plan,
    ):
        account_repo = InMemoryUserAccountRepository([user_account])
        plan_repo = InMemoryPlanRepository([basic_plan])
        subscription_repo = InMemorySubscriptionRepository()
        payment_gateway = create_autospec(PaymentGateway)
        payment_gateway.process_payment.return_value = Payment(success=True)

        use_case = SubscribeToPlanUseCase(
            payment_gateway=payment_gateway,
            notification_service=None,
            subscription_repository=subscription_repo,
            user_account_repository=account_repo,
            plan_repository=plan_repo,
        )
        input = SubscribeToPlanInput(
            user_id=user_account.id,
            plan_id=basic_plan.id,
            payment_token="payment_token123",
        )

        output = use_case.execute(input)

        created_subscription = subscription_repo.find_by_user_id(user_account.id)
        assert created_subscription.is_trial is False
        # assert output.subscription_id is not None
        assert output.subscription_id == created_subscription.id
        payment_gateway.process_payment.assert_called_once_with(
            payment_token="payment_token123",
            billing_address=user_account.billing_address,
        )

    def test_when_payment_fails_then_notify_and_create_trial_subscription(self):
        pass

    def test_when_user_does_not_exist_then_raise_user_does_not_exist_error(self):
        pass

    def test_when_plan_does_not_exist_then_raise_plan_not_found_error(self):
        pass

    def test_when_user_already_has_active_subscription_then_raise_subscription_conflict_error(
        self,
    ):
        pass