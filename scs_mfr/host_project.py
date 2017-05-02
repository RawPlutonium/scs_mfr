#!/usr/bin/env python3

"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

workflow:
  1: ./afe_calib -s SERIAL_NUMBER
  2: ./system_id.py -s VENDOR_ID MODEL_ID MODEL_NAME CONFIG SYSTEM_SERIAL
  3: ./api_auth.py -s ORG_ID API_KEY
  4: ./host_client.py -s -u USER_ID -l LAT LNG POSTCODE -p
> 5: ./host_project.py -s GROUP LOCATION_ID -p

Requires APIAuth, SystemID and AFECalib documents.

Creates Project document.

command line example:
./host_project.py -v -s field-trial 2 -p
"""

import sys

from scs_core.data.json import JSONify

from scs_core.gas.afe_calib import AFECalib

from scs_core.osio.client.api_auth import APIAuth
from scs_core.osio.config.project import Project
from scs_core.osio.config.project_topic import ProjectTopic
from scs_core.osio.data.topic import Topic
from scs_core.osio.data.topic_info import TopicInfo
from scs_core.osio.manager.topic_manager import TopicManager

from scs_core.sys.system_id import SystemID

from scs_host.client.http_client import HTTPClient
from scs_host.sys.host import Host

from scs_mfr.cmd.cmd_host_project import CmdHostProject


# --------------------------------------------------------------------------------------------------------------------

class HostProject(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, topic_manager):
        """
        Constructor
        """
        self.__topic_manager = topic_manager


    # ----------------------------------------------------------------------------------------------------------------

    def construct_topic(self, path, schema):
        topic = self.__topic_manager.find(path)

        if topic:
            updated = Topic(None, schema.name, schema.description, topic.is_public, topic.info, None, None)

            self.__topic_manager.update(topic.path, updated)

        else:
            info = TopicInfo(TopicInfo.FORMAT_JSON, None, None, None)     # for the v2 API, schema_id goes in Topic
            constructed = Topic(path, schema.name, schema.description, True, info, True, schema.schema_id)

            self.__topic_manager.create(constructed)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "HostProject:{topic_manager:%s}" % self.__topic_manager


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdHostProject()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit()


    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # APIAuth...
    api_auth = APIAuth.load_from_host(Host)

    if api_auth is None:
        print("APIAuth not available.", file=sys.stderr)
        exit()

    if cmd.verbose:
        print(api_auth, file=sys.stderr)


    # SystemID...
    system_id = SystemID.load_from_host(Host)

    if system_id is None:
        print("SystemID not available.", file=sys.stderr)
        exit()

    if cmd.verbose:
        print(system_id, file=sys.stderr)


    # AFECalib...
    afe_calib = AFECalib.load_from_host(Host)

    if afe_calib is None:
        print("AFECalib not available.", file=sys.stderr)
        exit()

    if cmd.verbose:
        print(afe_calib, file=sys.stderr)
        sys.stderr.flush()

    # manager...
    manager = TopicManager(HTTPClient(), api_auth.api_key)

    creator = HostProject(manager)

    # gases schema...
    gases_topic = ProjectTopic.find_gases_topic(afe_calib.gas_names())


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    # set...
    if cmd.set():
        project = Project.construct(api_auth.org_id, cmd.group, cmd.location_id)

        # existing gases topic...
        existing_gases_topics = manager.find_for_org(api_auth.org_id, project.gases_topic_path())
        existing_gases_topic = existing_gases_topics[0] if len(existing_gases_topics) else None

        if existing_gases_topic and existing_gases_topic.schema.id != gases_topic.schema_id:
            print("Existing gases schema (%d) does not match new gases schema (%d)." %
                  (existing_gases_topic.schema.id, gases_topic.schema_id), file=sys.stderr)
            exit()

        # set topics...
        creator.construct_topic(project.climate_topic_path(), ProjectTopic.CLIMATE)
        creator.construct_topic(project.gases_topic_path(), gases_topic)

        if cmd.particulates:
            creator.construct_topic(project.particulates_topic_path(), ProjectTopic.PARTICULATES)

        creator.construct_topic(project.status_topic_path(system_id), ProjectTopic.STATUS)
        creator.construct_topic(project.control_topic_path(system_id), ProjectTopic.CONTROL)

        project.save(Host)

    project = Project.load_from_host(Host)
    print(JSONify.dumps(project))

    # report...
    if cmd.verbose:
        print("-", file=sys.stderr)

        print("gases_topic:       %s" % gases_topic, file=sys.stderr)
        print("-", file=sys.stderr)

        found = manager.find(project.climate_topic_path())

        if found is not None:
            print("climate_topic:      %s" % found.path, file=sys.stderr)

        found = manager.find(project.gases_topic_path())

        if found is not None:
            print("gases_topic:        %s" % found.path, file=sys.stderr)

        found = manager.find(project.particulates_topic_path())

        if found is not None:
            print("particulates_topic: %s" % found.path, file=sys.stderr)

        found = manager.find(project.status_topic_path(system_id))

        if found is not None:
            print("status_topic:       %s" % found.path, file=sys.stderr)

        found = manager.find(project.control_topic_path(system_id))

        if found is not None:
            print("control_topic:      %s" % found.path, file=sys.stderr)
