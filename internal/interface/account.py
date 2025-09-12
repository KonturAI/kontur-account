from abc import abstractmethod
from typing import Protocol

from fastapi.responses import JSONResponse

from internal import model


class IOrganizationController(Protocol):
    @abstractmethod
    async def create_organization(
            self,
            name: str
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def get_organization_by_id(self, organization_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_organization_by_employee_id(self, employee_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_all_organizations(self) -> JSONResponse:
        pass

    @abstractmethod
    async def update_organization(
            self,
            organization_id: int,
            name: str = None,
            autoposting_moderation: bool = None
    ) -> JSONResponse:
        pass

    @abstractmethod
    async def delete_organization(self, organization_id: int) -> JSONResponse:
        pass


class IOrganizationService(Protocol):
    @abstractmethod
    async def create_organization(
            self,
            name: str,
            autoposting_moderation: bool = True
    ) -> int:
        pass

    @abstractmethod
    async def get_organization_by_id(self, organization_id: int) -> model.Organization:
        pass

    @abstractmethod
    async def get_organization_by_employee_id(self, employee_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_all_organizations(self) -> list[model.Organization]:
        pass

    @abstractmethod
    async def update_organization(
            self,
            organization_id: int,
            name: str = None,
            autoposting_moderation: bool = None
    ) -> None:
        pass

    @abstractmethod
    async def delete_organization(self, organization_id: int) -> None:
        pass


class IOrganizationRepo(Protocol):
    @abstractmethod
    async def create_organization(
            self,
            name: str,
            autoposting_moderation: bool = True
    ) -> int:
        pass

    @abstractmethod
    async def get_organization_by_id(self, organization_id: int) -> list[model.Organization]:
        pass

    @abstractmethod
    async def get_organization_by_employee_id(self, employee_id: int) -> JSONResponse:
        pass

    @abstractmethod
    async def get_all_organizations(self) -> list[model.Organization]:
        pass

    @abstractmethod
    async def update_organization(
            self,
            organization_id: int,
            name: str = None,
            autoposting_moderation: bool = None
    ) -> None:
        pass

    @abstractmethod
    async def delete_organization(self, organization_id: int) -> None:
        pass