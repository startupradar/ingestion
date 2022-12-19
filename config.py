import os

from core.api import DISCOVERY_ENDPOINTS, DiscoveryEndpointSource, SimilarStartupsSource
from core.workflow import CSVWorkflow

API_KEY = os.environ["STARTUPRADAR_API_KEY"]

# set up default workflow
sources = [
    # use all discovery endpoints
    *[DiscoveryEndpointSource(de) for de in DISCOVERY_ENDPOINTS],
    # add list of related domains
    SimilarStartupsSource(["startupradar.co"]),
]
WORKFLOW = CSVWorkflow(sources, ".out/")
