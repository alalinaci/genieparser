import re
import unittest
from unittest.mock import Mock

from pyats.topology import Device

from genie.metaparser.util.exceptions import SchemaEmptyParserError, \
                                             SchemaMissingKeyError

from genie.libs.parser.iosxr.show_redundancy import ShowRedundancy


#############################################################################
# unitest For show redundancy
#############################################################################

class test_show_redundancy(unittest.TestCase):

    device = Device(name='aDevice')

    empty_output = {'execute.return_value': ''}

    golden_parsed_output = {
   "node":{
      "0/RP0/CPU0":{
         "role":"ACTIVE",
         "ready":"NSR-ready",
         "last_reload_timestamp":"Thu Nov  5 05:12:51 2020",
         "time_since_last_reload":"24 weeks, 3 days, 22 hours, 49 minutes ago",
         "node_uptime_timestamp":"Sat Nov  7 09:42:00 2020",
         "node_uptime":"24 weeks, 1 day, 18 hours, 20 minutes",
         "node_uptime_in_seconds":152400,
         "last_switchover_timepstamp":"Mon Nov 30 05:30:53 2020",
         "time_since_last_switchover":"20 weeks, 6 days, 22 hours, 31 minutes ago",
         "standby_node_timestamp":"Mon Nov 30 05:35:47 2020",
         "time_since_standby_boot":"20 weeks, 6 days, 22 hours, 26 minutes ago",
         "standby_node_not_ready":"Tue Apr 20 01:28:51 2021",
         "time_since_standby_node_not_ready":"6 days, 2 hours, 33 minutes ago",
         "standby_node_ready":"Tue Apr 20 01:28:51 2021",
         "time_since_standby_node_ready":"6 days, 2 hours, 33 minutes ago"
      }
   }
}

    golden_output = {'execute.return_value': '''
    Mon Apr 26 04:02:05.027 UTC
    Redundancy information for node 0/RP0/CPU0:
    ==========================================
    Node 0/RP0/CPU0 is in ACTIVE role
    Partner node (0/RP1/CPU0) is in STANDBY role
    Standby node in 0/RP1/CPU0 is ready
    Standby node in 0/RP1/CPU0 is NSR-ready

    Reload and boot info
    ----------------------
    A99-RP3-16G reloaded Thu Nov  5 05:12:51 2020: 24 weeks, 3 days, 22 hours, 49 minutes ago
    Active node booted Sat Nov  7 09:42:00 2020: 24 weeks, 1 day, 18 hours, 20 minutes ago
    Last switch-over Mon Nov 30 05:30:53 2020: 20 weeks, 6 days, 22 hours, 31 minutes ago
    Standby node boot Mon Nov 30 05:35:47 2020: 20 weeks, 6 days, 22 hours, 26 minutes ago
    Standby node last went not ready Tue Apr 20 01:28:51 2021: 6 days, 2 hours, 33 minutes ago
    Standby node last went ready Tue Apr 20 01:28:51 2021: 6 days, 2 hours, 33 minutes ago
    Standby node last went not NSR-ready Tue Apr 20 01:31:54 2021: 6 days, 2 hours, 30 minutes ago
    Standby node last went NSR-ready Tue Apr 20 01:31:54 2021: 6 days, 2 hours, 30 minutes ago
    There have been 2 switch-overs since reload

    Active node reload "Initiating switch-over."
    Standby node reload "Initiating switch-over. "
    '''}

    def test_show_redundancy(self):
        self.device = Mock(**self.empty_output)
        obj = ShowRedundancy(device=self.device)
        with self.assertRaises(SchemaEmptyParserError):
            parsed_output = obj.parse()

    def test_show_redundancy(self):
        self.device = Mock(**self.golden_output_brief)
        obj = ShowRedundancy(device=self.device)
        parsed_output = obj.parse()
        self.assertEqual(parsed_output, self.golden_parsed_output_brief)

if __name__ == '__main__':
    unittest.main()