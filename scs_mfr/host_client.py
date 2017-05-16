#!/usr/bin/env python3

"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

SCS workflow:
    1: ./afe_calib -s AFE_SERIAL_NUMBER
    2: ./afe_baseline.py -v -1 SN1_OFFSET -2 SN2_OFFSET -3 SN3_OFFSET -4 SN3_OFFSET

OpenSensors workflow:
    1: ./host_id.py
    2: ./system_id.py -s VENDOR_ID MODEL_ID MODEL_NAME CONFIG SYSTEM_SERIAL_NUMBER
    3: ./api_auth.py -s ORG_ID API_KEY
(   4: ./host_organisation.py -o ORG_ID -n NAME -w WEB -d DESCRIPTION -e EMAIL -v )
  > 5: ./host_client.py -s -u USER_ID -l LAT LNG POSTCODE -p
    6: ./host_project.py -s GROUP LOCATION_ID -p

Requires APIAuth and SystemID documents.

Creates ClientAuth document.

command line example:
./host_client.py -s -u south-coast-science-test-user -l 50.823130 -0.122922 "BN2 0DF" -p -v
"""

import sys

from scs_core.data.json import JSONify

from scs_core.gas.afe_calib import AFECalib

from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.client.client_auth import ClientAuth
from scs_core.osio.config.project_source import ProjectSource
from scs_core.osio.manager.device_manager import DeviceManager
from scs_core.osio.manager.user_manager import UserManager

from scs_core.sys.system_id import SystemID

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host

from scs_mfr.cmd.cmd_host_client import CmdHostClient


# TODO: maybe we should use the device-type field?

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # APIAuth...
    api_auth = APIAuth.load_from_host(Host)

    if api_auth is None:
        print("APIAuth not available.", file=sys.stderr)
        exit()

    # SystemID...
    system_id = SystemID.load_from_host(Host)

    if system_id is None:
        print("SystemID not available.", file=sys.stderr)
        exit()

    # AFECalib...
    afe_calib = AFECalib.load_from_host(Host)

    if afe_calib is None:
        print("AFECalib not available.", file=sys.stderr)
        exit()

    # User manager...
    user_manager = UserManager(HTTPClient(), api_auth.api_key)

    # Device manager...
    device_manager = DeviceManager(HTTPClient(), api_auth.api_key)

    # check for existing registration...
    device = device_manager.find_for_name(api_auth.org_id, system_id.box_label())


    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdHostClient()

    if cmd.verbose:
        print(cmd, file=sys.stderr)
        print(api_auth, file=sys.stderr)
        print(system_id, file=sys.stderr)
        print(afe_calib, file=sys.stderr)
        sys.stderr.flush()

    if not cmd.is_valid(device):
        cmd.print_help(sys.stderr)
        exit()


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    if cmd.set():
        # User...
        if cmd.user_id:
            user = user_manager.find_public(cmd.user_id)

            if user is None:
                print("User not available.", file=sys.stderr)
                exit()

        # tags...
        tags = ProjectSource.tags(afe_calib, cmd.particulates)

        if device:
            if cmd.user_id:
                print("Device owner-id cannot be updated.", file=sys.stderr)
                exit()

            # find ClientAuth...
            client_auth = ClientAuth.load_from_host(Host)

            # update Device...
            updated = ProjectSource.update(device, cmd.lat, cmd.lng, cmd.postcode, cmd.description, tags)
            device_manager.update(api_auth.org_id, device.client_id, updated)

            # find updated device...
            device = device_manager.find(api_auth.org_id, device.client_id)

        else:
            # create Device...
            device = ProjectSource.create(system_id, api_auth, cmd.lat, cmd.lng, cmd.postcode, cmd.description, tags)
            device = device_manager.create(cmd.user_id, device)

            # create ClientAuth...
            client_auth = ClientAuth(cmd.user_id, device.client_id, device.password)
            client_auth.save(Host)

    else:
        # find ClientAuth...
        client_auth = ClientAuth.load_from_host(Host)

    if cmd.verbose:
        print(client_auth, file=sys.stderr)

    print(JSONify.dumps(device))
