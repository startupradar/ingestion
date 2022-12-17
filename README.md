# StartupRadar Use Case: Ingestion

This use case gives you a framework on how to ingest StartupRadar data into your own systems.

- fetch data from a variety of sources
- compare against already stored data
- crate new deals or update existing ones


## Supported Backends
Backends are the places where existing deals can be found and where new deals can get stored.

File-based:

- CSV

CRMs (coming soon):

- Pipedrive
- Hubspot
- Affinity
- Salesforce
- Attio

Other (coming soon):

- Airtable
- Slack
- Asana
- Trello


## How to use
- install by cloning this repository
- create a virtual environment and activate it
- install its requirements: `pip install -r requirements.txt`
- configure your storage
- set your API key


## Changelog

### 2022-12-17
- initial publication