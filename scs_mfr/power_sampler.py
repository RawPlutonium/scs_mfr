#!/usr/bin/env python3

"""
Created on 2 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./scs_manufacture/power_sampler.py -i 2 -n 10
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sample.sample_datum import SampleDatum
from scs_core.sync.sampler import Sampler
from scs_core.sys.exception_report import ExceptionReport

from scs_mfr.cmd.cmd_scalar import CmdScalar
from scs_mfr.power.power_meter import PowerMeter


# --------------------------------------------------------------------------------------------------------------------

class PowerSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, interval, sample_count=0):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__meter = PowerMeter()
        self.__meter.reset()

        self.reset_timer()


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return 'pow', self.__meter.sample


    def close(self):
        self.__meter.close()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "PowerSampler:{meter:%s}" % self.__meter


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    sampler = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdScalar(0.5)

        if cmd.verbose:
            print(cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resource...

        sampler = PowerSampler(cmd.interval, cmd.samples)

        if cmd.verbose:
            print(sampler, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        for power_datum in sampler.samples():
            recorded = LocalizedDatetime.now()
            datum = SampleDatum(recorded, power_datum)

            print(JSONify.dumps(datum))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt as ex:
        if cmd.verbose:
            print("power_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if sampler:
            sampler.close()