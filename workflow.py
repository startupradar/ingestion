from abc import ABC

from api import DiscoveryEndpointSource, SimilarStartupsSource
from backends.files import PandasExportDealStorage


class Workflow(ABC):
    sources = None
    storage = None


class CSVWorkflow(Workflow):
    def __init__(self, endpoints, output_directory=".out/"):
        # set up sources
        self.sources = [
            # use all discovery endpoints
            *[DiscoveryEndpointSource(de) for de in endpoints],
            # add list of related domains
            SimilarStartupsSource(["karllorey.com"]),
        ]

        # set up storage
        self.storage = PandasExportDealStorage(output_directory)
