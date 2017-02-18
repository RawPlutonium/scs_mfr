"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

example document:
{"org-id": "south-coast-science-dev", "api-key": "43308b72-ad41-4555-b075-b4245c1971db"}
"""

import optparse


# --------------------------------------------------------------------------------------------------------------------

class CmdOSIOAPIAuth(object):
    """unix command line handler"""

    def __init__(self):
        """
        Constructor
        """
        self.__parser = optparse.OptionParser(usage="%prog [-s ORG_ID API_KEY] [-v]", version="%prog 1.0")

        # optional...
        self.__parser.add_option("--set", "-s", type="string", nargs=2, action="store", dest="org_key",
                                 help="org ID and API key")

        self.__parser.add_option("--verbose", "-v", action="store_true", dest="verbose", default=False,
                                 help="report narrative to stderr")

        self.__opts, self.__args = self.__parser.parse_args()


    # ----------------------------------------------------------------------------------------------------------------

    def set(self):
        return self.__opts.org_key is not None


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def org_id(self):
        return self.__opts.org_key[0] if self.__opts.org_key else None


    @property
    def api_key(self):
        return self.__opts.org_key[1] if self.__opts.org_key else None


    @property
    def verbose(self):
        return self.__opts.verbose


    @property
    def args(self):
        return self.__args


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "CmdOSIOAPIAuth:{org_id:%s, api_key:%s, verbose:%s, args:%s}" % \
               (self.org_id, self.api_key, self.verbose, self.args)