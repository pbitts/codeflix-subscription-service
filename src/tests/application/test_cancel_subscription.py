from unittest.mock import create_autospec
import uuid

import pytest

from src.application.cancel_subscription import CancelSubscriptionUseCase, CancelSubscriptionInput
from src.application.exceptions import SubscriptionNotFoundError
from src.domain.subscription import Subscription, SubscriptionStatus
from src.tests.infra.in_memory_subscription_repository import InMemorySubscriptionRepository



class TestCancelSubscription:
    def test_when_subscription_not_found_then_raise_error(self):
        repo = InMemorySubscriptionRepository()

        use_case = CancelSubscriptionUseCase(
            repo
        )

        subs_id = uuid.uuid4()
        input = CancelSubscriptionInput(subscription_id=subs_id)
        with pytest.raises(SubscriptionNotFoundError):
            use_case.execute(input=input)

    def test_cancel_subscription(self):
        repo = InMemorySubscriptionRepository()
        user_id = uuid.uuid4()
        plan_id = uuid.uuid4()
        subscription = Subscription.create_regular(user_id, plan_id)
        repo.save(subscription)
        
        saved_subs  = repo.find_by_id(subscription.id)
        assert saved_subs is not None
        assert repo.find_by_user_id(user_id) is not None
        assert saved_subs.status == SubscriptionStatus.ACTIVE

        use_case = CancelSubscriptionUseCase(
            repo
        )

        input = CancelSubscriptionInput(subscription_id=subscription.id)
        use_case.execute(input=input)
        
        cancelled_subs = repo.find_by_id(subscription.id)
        assert cancelled_subs.status == SubscriptionStatus.CANCELLED
        
        