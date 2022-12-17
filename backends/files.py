"""
File-based storage.
"""
import logging
import os
import typing
from datetime import datetime, date
from pathlib import Path

import pandas as pd

from base import Deal, DealStorage


class PandasDeal(Deal):
    def __init__(self, file_date: date):
        # for pandas frame, we only know the creation date
        self.created_at = file_date
        self.last_activity = file_date

    def add_note(self, note: str):
        raise RuntimeError("For file-based deals, creating notes is not possible")

    def __repr__(self):
        return f"<PandasDeal {self.created_at=}>"


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
                created_at = datetime.fromtimestamp(timestamp_creation).date()
                deals.append(PandasDeal(created_at))
        return deals

    def add_deal(self, title, domain):
        self.domains_to_store.append(domain)

    def sync(self) -> None:
        filename = date.today().strftime("%Y-%m-%d") + ".csv"
        file_path = self.directory.joinpath(filename)

        # abort if file exists
        if file_path.exists():
            error_msg = f"Output file already exists, delete manually if necessary ({file_path=})"
            raise RuntimeError(error_msg)

        df = pd.DataFrame(self.domains_to_store, columns=["domain"])
        df.to_csv(file_path)

        self.domains_to_store = []
