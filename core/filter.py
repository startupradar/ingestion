"""
Filters to sort out undesired startups.
"""
from abc import ABC


class Filter(ABC):
    def is_filtered(self, domain):
        return False

    def filter(self, domains):
        for domain in domains:
            if not self.is_filtered(domain):
                yield domain
