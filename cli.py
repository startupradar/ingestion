import logging

import config
from core.workflow import Workflow


def get_workflow() -> Workflow:
    return config.WORKFLOW


def run(dry_run=False):
    """
    Run configuration.
    :param dry_run: do not store any data
    :return:
    """
    workflow = get_workflow()

    # fetch new domains from sources
    domains_fetched = set()
    for source in workflow.sources:
        logging.info(f"fetching source ({source=})")
        domains_fetched |= set(source.get_domains())
    logging.info(f"fetched domains ({len(domains_fetched)=})")

    # check against deal storage
    domains_to_push = []
    for domain in domains_fetched:
        deals_with_domain = workflow.storage.find_deals_by_domain(domain)
        if deals_with_domain:
            logging.info(
                f"deal for domain already exists ({domain=}, {deals_with_domain=})"
            )
        else:
            logging.info(f"deal is new ({domain=})")
            domains_to_push.append(domain)

    # push new deals to storage
    for domain_to_push in domains_to_push:
        workflow.storage.add_deal(title=domain_to_push, domain=domain_to_push)

    if dry_run:
        logging.info("skipping actual sync here")
    else:
        workflow.storage.sync()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
