"""
Created on 18 May 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys
import time
import tzlocal

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.data.rtc_datetime import RTCDatetime

from scs_dfe.time.ds1338 import DS1338

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

from scs_mfr.test.test import Test


# --------------------------------------------------------------------------------------------------------------------

class RTCTest(Test):
    """
    test script
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, verbose):
        Test.__init__(self, verbose)


    # ----------------------------------------------------------------------------------------------------------------

    def conduct(self):
        if self.verbose:
            print("RTC...", file=sys.stderr)

        try:
            I2C.open(Host.I2C_SENSORS)

            # resources...
            now = LocalizedDatetime.now()

            DS1338.init()

            # test...
            rtc_datetime = RTCDatetime.construct_from_localized_datetime(now)
            DS1338.set_time(rtc_datetime)

            time.sleep(2)

            rtc_datetime = DS1338.get_time()
            localized_datetime = rtc_datetime.as_localized_datetime(tzlocal.get_localzone())

            self.datum = localized_datetime - now

            if self.verbose:
                print(self.datum, file=sys.stderr)

            # test criterion...
            return 1 <= self.datum.seconds <= 2

        finally:
            I2C.close()
