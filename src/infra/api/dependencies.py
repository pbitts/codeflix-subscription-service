from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from src.application.create_plan import CreatePlanUseCase
from src.application.create_user_account import CreateUserAccountUseCase
from src.application.subscribe_to_plan import SubscribeToPlanUseCase
from src.domain.repositories import (
    PlanRepository,
    UserAccountRepository,
    SubscriptionRepository,
)
from src.infra.auth import AuthService
from src.infra.auth.in_memory_auth_service import InMemoryAuthService
from src.infra.db import (
    get_session,
    SQLModelPlanRepository,
    SQLModelUserAccountRepository,
)
from src.infra.db.repositories.sql_model_subscription_repository import (
    SQLModelSubscriptionRepository,
)
from src.infra.notification.console_notification_service import (
    ConsoleNotificationService,
)
from src.infra.notification.notification_service import NotificationService
from src.infra.payment.fake_payment_gateway import FakePaymentGateway
from src.infra.payment.payment_gateway import PaymentGateway

# Database
SessionDep = Annotated[Session, Depends(get_session)]


# Repositories
def get_plan_repository(session: SessionDep) -> PlanRepository:
    return SQLModelPlanRepository(session)


def get_user_account_repository(session: SessionDep) -> UserAccountRepository:
    return SQLModelUserAccountRepository(session)


def get_subscription_repository(session: SessionDep) -> SubscriptionRepository:
    return SQLModelSubscriptionRepository(session)


PlanRepositoryDep = Annotated[PlanRepository, Depends(get_plan_repository)]
UserAccountRepositoryDep = Annotated[
    UserAccountRepository, Depends(get_user_account_repository)
]
SubscriptionRepositoryDep = Annotated[
    SubscriptionRepository, Depends(get_subscription_repository)
]


# External dependencies
def get_auth_service() -> AuthService:
    return InMemoryAuthService()  # TODO: replace by KeycloakAuthService


def get_notification_service() -> NotificationService:
    return ConsoleNotificationService()  # TODO: EmailNotificationService


def get_payment_gateway() -> PaymentGateway:
    return FakePaymentGateway()


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
NotificationServiceDep = Annotated[
    NotificationService, Depends(get_notification_service)
]
PaymentGatewayDep = Annotated[PaymentGateway, Depends(get_payment_gateway)]


# Use cases
def get_create_plan_use_case(plan_repository: PlanRepositoryDep) -> CreatePlanUseCase:
    return CreatePlanUseCase(plan_repository)


def get_create_user_account_use_case(
    auth_service: AuthServiceDep,
    user_account_repository: UserAccountRepositoryDep,
) -> CreateUserAccountUseCase:
    return CreateUserAccountUseCase(auth_service, user_account_repository)


def get_subscribe_to_plan_use_case(
    payment_gateway: PaymentGatewayDep,
    notification_service: NotificationServiceDep,
    subscription_repository: SubscriptionRepositoryDep,
    user_account_repository: UserAccountRepositoryDep,
    plan_repository: PlanRepositoryDep,
) -> SubscribeToPlanUseCase:
    return SubscribeToPlanUseCase(
        payment_gateway,
        notification_service,
        subscription_repository,
        user_account_repository,
        plan_repository,
    )


CreatePlanUseCaseDep = Annotated[CreatePlanUseCase, Depends(get_create_plan_use_case)]
CreateUserAccountUseCaseDep = Annotated[
    CreateUserAccountUseCase, Depends(get_create_user_account_use_case)
]
SubscribeToPlanUseCaseDep = Annotated[
    SubscribeToPlanUseCase, Depends(get_subscribe_to_plan_use_case)
]