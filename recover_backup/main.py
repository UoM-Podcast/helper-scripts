#!/usr/bin/env python3

""" This module contains the main method. """
import sys
import os

sys.path.append(os.path.join(os.path.abspath('..'), "lib"))

from input.check_recovery_start import check_recovery_start
from input.parse_args import parse_args
from recover.find_media_packages import find_media_packages
from recover.recover import recover_mp
from args.url_builder import DEFAULT_TENANT, URLBuilder
from data_handling.errors import MediaPackageError
from rest_requests.request_error import RequestError


def main():
    """
    Parse the arguments, get media packages for recovery and check these for correctness before attempting to recover
    them.
    """

    # parse arguments
    opencast, https, digest_login, backup, media_packages, tenant, workflow_id, last_version = parse_args()

    if not tenant:
        print("No tenant provided, using default tenant.")
        tenant = DEFAULT_TENANT
    if last_version:
        print("Always using last version of media packages.")

    url_builder = URLBuilder(opencast, https)
    base_url = url_builder.get_base_url(tenant)

    # get paths to media packages to be recovered
    mps_to_recover = find_media_packages(backup, tenant, last_version, media_packages)

    if not mps_to_recover:
        # abort recovery
        print("There are no media packages that can be recovered.")
        sys.exit()

    # check if these should be recovered
    start_recovery = check_recovery_start(mps_to_recover)

    if not start_recovery:
        # abort recovery
        print("Okay, not recovering anything.")
        sys.exit()

    else:
        # start recovery
        print("Starting recovery process.")

        for mp in mps_to_recover:

            try:
                workflow = recover_mp(mp, base_url, digest_login, workflow_id)
                print("Recovered media package {} (new id: {}) and started workflow {} with id {}.".
                      format(mp.id, workflow.mp_id, workflow.template, workflow.id))
            except MediaPackageError as e:
                print("Media package {} could not be recovered: {}".format(mp.id, str(e)))
            except RequestError as e:
                print("Media package {} could not be recovered: {}".format(mp.id, e.error))
            except Exception as e:
                print("Media package {} could not be recovered: {}".format(mp.id, str(e)))

        print("Finished.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborting script.")
        sys.exit(0)
