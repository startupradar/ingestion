import typing
from abc import ABC

from backends.files import PandasExportDealStorage
from core.api import DomainSource


class Workflow(ABC):
    sources = None
    storage = None


class CSVWorkflow(Workflow):
    def __init__(self, sources: typing.List[DomainSource], output_directory=".out/"):
        # set up sources
        self.sources = sources

        # set up storage
        self.storage = PandasExportDealStorage(output_directory)
