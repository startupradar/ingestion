import datetime
import logging
import os
import typing
from abc import ABC
from pathlib import Path

import pandas as pd
import requests


API_KEY = os.environ["STARTUPRADAR_API_KEY"]


class Deal(ABC):
    """
    Representation of a deal, e.g. in a CRM.
    """

    created_at: datetime.date = None
    last_activity: datetime.date = None

    def add_note(self, note: str):
        raise NotImplementedError()


class PandasDeal(Deal):
    def __init__(self, file_date: datetime.date):
        # for pandas frame, we only know the creation date
        self.created_at = file_date
        self.last_activity = file_date

    def add_note(self, note: str):
        raise RuntimeError("For file-based deals, creating notes is not possible")

    def __repr__(self):
        return f"<PandasDeal {self.created_at=}>"


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


class PandasExportDealStorage(DealStorage):
    """
    This is a pandas-based CSV export of deals.
    """

    def __init__(self, directory):
        self.directory = Path(directory)

        if not self.directory.exists():
            logging.warning(f"creating export directory ({self.directory=})")
            self.directory.mkdir(parents=True, exist_ok=True)

        self.domains_to_store = []

    def get_filenames(self) -> typing.List[str]:
        return os.listdir(self.directory)

    def get_dataframes(self) -> typing.List[pd.DataFrame]:
        return [
            pd.read_csv(self.directory.joinpath(filename))
            for filename in self.get_filenames()
        ]

    def find_deals_by_domain(self, domain: str) -> typing.List[Deal]:
        deals = []
        for filename, df in zip(self.get_filenames(), self.get_dataframes()):
            if domain in df["domain"].values:
                file_path = self.directory.joinpath(filename)
                timestamp_creation = file_path.lstat().st_ctime
                created_at = datetime.datetime.fromtimestamp(timestamp_creation).date()
                deals.append(PandasDeal(created_at))
        return deals

    def add_deal(self, title, domain):
        self.domains_to_store.append(domain)

    def sync(self) -> None:
        filename = datetime.date.today().strftime("%Y-%m-%d") + ".csv"
        file_path = self.directory.joinpath(filename)

        # abort if file exists
        if file_path.exists():
            error_msg = f"Output file already exists, delete manually if necessary ({file_path=})"
            raise RuntimeError(error_msg)

        df = pd.DataFrame(self.domains_to_store, columns=["domain"])
        df.to_csv(file_path)

        self.domains_to_store = []


class DomainSource(ABC):
    def generate_domains(self) -> typing.Generator:
        raise NotImplementedError()

    def get_domains(self) -> typing.List[str]:
        return list(self.generate_domains())


DISCOVERY_ENDPOINTS = [
    "in-the-press",
    "linked-from-sources",
    "academic-links",
    "firehose",
]


class DiscoveryEndpointSource(DomainSource):
    def __init__(self, endpoint: str):
        if endpoint not in DISCOVERY_ENDPOINTS:
            error_msg = f"unknown endpoint ({endpoint=}, {DISCOVERY_ENDPOINTS=})"
            raise RuntimeError(error_msg)

        self.url = f"https://api.startupradar.co/discovery/{endpoint}"
        self.api_key = API_KEY

    def generate_domains(self) -> typing.Generator:
        resp = requests.get(self.url, headers={"X-ApiKey": self.api_key})
        assert resp.status_code == 200
        return (link["to_domain"] for link in resp.json())

    def __repr__(self):
        return f"<DiscoveryEndpoint {self.url=}>"


class SimilarStartupsSource(DomainSource):
    """
    Finds similar startups based on a list of existing startups.
    """

    def __init__(self, domains: typing.List[str]):
        self.domains = set(domains)
        self.api_key = API_KEY

    def generate_domains(self) -> typing.Generator:
        for domain in self.domains:
            url = f"https://api.startupradar.co/web/domains/{domain}/similar"
            resp = requests.get(url, headers={"X-ApiKey": self.api_key})
            assert resp.status_code == 200
            for d_obj in resp.json():
                yield d_obj["domain"]


def cli():
    # define where deals are stored
    deal_storage = PandasExportDealStorage(".out/")

    # define where new deals are discovered
    discovery_sources = [DiscoveryEndpointSource(de) for de in DISCOVERY_ENDPOINTS]
    sources: typing.List[DomainSource] = discovery_sources

    similar_domains_file_path = Path(".in/similar.txt")
    if similar_domains_file_path.exists():
        domains_related = similar_domains_file_path.read_text().split("\n")
        sources.append(SimilarStartupsSource(domains_related))

    # fetch new domains from sources
    domains_fetched = set()
    for source in sources:
        logging.info(f"fetching source ({source=})")
        domains_fetched |= set(source.get_domains())
    logging.info(f"fetched domains ({len(domains_fetched)=})")

    # check against deal storage
    domains_to_push = []
    for domain in domains_fetched:
        deals_with_domain = deal_storage.find_deals_by_domain(domain)
        if deals_with_domain:
            logging.info(
                f"deal for domain already exists ({domain=}, {deals_with_domain=})"
            )
        else:
            logging.info(f"deal is new ({domain=})")
            domains_to_push.append(domain)

    # push new deals to storage
    for domain_to_push in domains_to_push:
        deal_storage.add_deal(title=domain_to_push, domain=domain_to_push)

    deal_storage.sync()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli()
