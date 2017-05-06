#!/usr/bin/env python3

"""
Created on 8 Mar 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

SCS workflow:
    1: ./afe_calib -s AFE_SERIAL_NUMBER
    2: ./afe_baseline.py -v -1 SN1_OFFSET -2 SN2_OFFSET -3 SN3_OFFSET -4 SN3_OFFSET

OpenSensors workflow:
    1: ./host_id.py
    2: ./system_id.py -s VENDOR_ID MODEL_ID MODEL_NAME CONFIG SYSTEM_SERIAL_NUMBER
    3: ./api_auth.py -s ORG_ID API_KEY
( > 4: ./host_organisation.py -o ORG_ID -n NAME -w WEB -d DESCRIPTION -e EMAIL -v )
    5: ./host_client.py -s -u USER_ID -l LAT LNG POSTCODE -p
    6: ./host_project.py -s GROUP LOCATION_ID -p

Requires APIAuth document.

Note: the APIAuth document arguably should be updated by this script, but currently it is not.

command line example:
./host_organisation.py \
-o south-coast-science-dev \
-n 'South Coast Science (Dev)' \
-w https://www.southcoastscience.com \
-d 'development operations for South Coast Science air quality monitoring instruments' \
-e bruno.beloff@southcoastscience.com
"""

import sys

from scs_core.data.json import JSONify
from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.data.organisation import Organisation
from scs_core.osio.manager.organisation_manager import OrganisationManager

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host

from scs_mfr.cmd.cmd_host_organisation import CmdHostOrganisation


# TODO: Update the APIAuth document, as necessary

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # APIAuth...
    api_auth = APIAuth.load_from_host(Host)

    if api_auth is None:
        print("APIAuth not available.", file=sys.stderr)
        exit()

    # manager...
    manager = OrganisationManager(HTTPClient(), api_auth.api_key)

    # check for existing registration...
    org = manager.find(api_auth.org_id)


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdHostOrganisation()

    if not cmd.is_valid(org):
        cmd.print_help(sys.stderr)
        exit()

    if cmd.verbose:
        print(api_auth, file=sys.stderr)
        print(cmd, file=sys.stderr)
        sys.stderr.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    if cmd.set():
        if org:
            name = org.name if cmd.name is None else cmd.name
            website = org.website if cmd.website is None else cmd.website
            description = org.description if cmd.description is None else cmd.description
            email = org.email if cmd.email is None else cmd.email

            # update Organisation...
            updated = Organisation(None, name, website, description, email)
            manager.update(org.id, updated)

            org = manager.find(org.id)

        else:
            if not cmd.is_complete():
                cmd.print_help(sys.stderr)
                exit()

            # create Organisation...
            org = Organisation(cmd.org_id, cmd.name, cmd.website, cmd.description, cmd.email)
            manager.create(org)

    else:
        # find self...
        org = manager.find(api_auth.org_id)

    print(JSONify.dumps(org))
