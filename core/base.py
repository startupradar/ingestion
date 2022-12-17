import typing
from abc import ABC
from datetime import datetime


class Deal(ABC):
    """
    Representation of a deal, e.g. in a CRM.
    """

    created_at: datetime.date = None
    last_activity: datetime.date = None

    def add_note(self, note: str):
        raise NotImplementedError()


class DealStorage(ABC):
    """
    A place where deals are stored, e.g. a CRM.
    """

    def find_deals_by_domain(self, domain: str) -> typing.List[Deal]:
        raise NotImplementedError()

    def add_deal(self, title, domain):
        raise NotImplementedError()

    def sync(self) -> None:
        """
        Run a sync, i.e. push new deals and notes.
        """
        raise NotImplementedError()


class DomainSource(ABC):
    def generate_domains(self) -> typing.Generator:
        raise NotImplementedError()

    def get_domains(self) -> typing.List[str]:
        return list(self.generate_domains())
