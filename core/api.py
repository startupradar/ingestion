import typing

import requests

import config
from base import DomainSource

DISCOVERY_ENDPOINTS = [
    "in-the-press",
    "linked-from-sources",
    "academic-links",
    "firehose",
]


def _request(url):
    resp = requests.get(url, headers={"X-ApiKey": config.API_KEY})
    assert resp.status_code == 200, f"failed ({resp.status_code=}, {resp.json()})"
    return resp.json()


class DiscoveryEndpointSource(DomainSource):
    def __init__(self, endpoint: str):
        if endpoint not in DISCOVERY_ENDPOINTS:
            error_msg = f"unknown endpoint ({endpoint=}, {DISCOVERY_ENDPOINTS=})"
            raise RuntimeError(error_msg)

        self.url = f"https://api.startupradar.co/discovery/{endpoint}"

    def generate_domains(self) -> typing.Generator:
        response = _request(self.url)
        return (link["to_domain"] for link in response)

    def __repr__(self):
        return f"<DiscoveryEndpoint {self.url=}>"


class SimilarStartupsSource(DomainSource):
    """
    Finds similar startups based on a list of existing startups.
    """

    def __init__(self, domains: typing.List[str]):
        self.domains = set(domains)

    def generate_domains(self) -> typing.Generator:
        for domain in self.domains:
            url = f"https://api.startupradar.co/web/domains/{domain}/similar"
            resp = _request(url)
            for d_obj in resp:
                yield d_obj["domain"]
