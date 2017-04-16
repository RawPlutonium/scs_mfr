"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdHostProject(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-s GROUP LOCATION_ID [-p]] [-v]",
                                              version="%prog 1.0")

        # optional...
        self.__parser.add_option("--set", "-s", type="string", nargs=2, action="store", dest="group_location",
                                 help="set topic group and location ID")

        self.__parser.add_option("--particulates", "-p", action="store_true", dest="particulates",
                                 help="include particulates topic")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def is_valid(self):
        if self.__opts.group_location is not None:
            try:
                int(self.__opts.group_location[1])
            except ValueError:
                return False

        if self.__opts.group_location is None:
            return self.particulates is None

        return True


    # ----------------------------------------------------------------------------------------------------------------

    def set(self):
        return self.__opts.group_location is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def group(self):
        return self.__opts.group_location[0] if self.__opts.group_location is not None else None


    @property
    def location_id(self):
        return self.__opts.group_location[1] if self.__opts.group_location is not None else None


    @property
    def particulates(self):
        return self.__opts.particulates


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def print_help(self, file):
        self.__parser.print_help(file)


    def __str__(self, *args, **kwargs):
        return "CmdHostProject:{group:%s, location_id:%s, particulates:%s, verbose:%s, args:%s}" % \
               (self.group, self.location_id, self.particulates, self.verbose, self.args)
