#/pyats/working/genieparser/src/genie/libs/parser/iosxr/show_redundancy.py
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Schema, Any, Optional, Or
import re

# =======================================================
# Schema for `show redundancy`
# ========================================================
class ShowRedundancySchema(MetaParser):
    """Schema for show redundancy"""
    schema = {
        'node':
            {Any():
                {'role': str,
                 Optional('valid_partner'): str,
                 Optional('ready'): str,
                 Optional('group'):
                    {Any():
                        {'primary': str,
                         'backup': str,
                         'status': str,
                        },
                    },
                 Optional('primary_rmf_state'): str,
                 Optional('primary_rmf_state_reason'): str,
                 'last_reload_timestamp': str,
                 'time_since_last_reload': str,
                 'node_uptime': str,
                 'node_uptime_timestamp': str,
                 'node_uptime_in_seconds': int,
                 Optional('standby_node'): str,
                 Optional('backup_process'): str,
                 Optional('last_switchover_timepstamp'): str,
                 Optional('time_since_last_switchover'): str,
                 Optional('standby_node_timestamp'): str,
                 Optional('time_since_standby_boot'): str,
                 Optional('standby_node_not_ready'): str,
                 Optional('time_since_standby_node_not_ready'): str,
                 Optional('standby_node_ready'):str,
                 Optional('time_since_standby_node_ready'): str,
                 Optional('reload_cause'): str
                },
            },
        }

class ShowRedundancy(ShowRedundancySchema):
    """Parser for show redundancy"""
    cli_command = 'show redundancy'
    exclude = ['node_uptime', 'time_since_standby_boot',
        'time_since_last_reload', 'time_since_last_switchover',
        'time_since_standby_node_not_ready', 'time_since_standby_node_ready',
        'standby_node_not_ready', 'standby_node_ready',
        'standby_node_timestamp', 'node_uptime_in_seconds', 'iteration:']


    def cli(self,output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        # Init vars
        redundancy_dict = {}

        for line in out.splitlines():
            line = line.rstrip()

            # Redundancy information for node 0/RP0/CPU0
            p1 = re.compile(r'\s*Redundancy +information +for +node'
                             ' +(?P<node>[a-zA-Z0-9\/]+):$')
            m = p1.match(line)
            if m:
                if 'node' not in redundancy_dict:
                    redundancy_dict['node'] = {}
                node = str(m.groupdict()['node'])
                if node not in redundancy_dict['node']:
                    redundancy_dict['node'][node] = {}
                    continue

            # Node 0/RSP0/CPU0 is in ACTIVE role
            p2 = re.compile(r'\s*Node +([a-zA-Z0-9\/]+) +is +in'
                             ' +(?P<role>[a-zA-Z]+) +role$')
            m = p2.match(line)
            if m:
                redundancy_dict['node'][node]['role'] = \
                    str(m.groupdict()['role'])
                continue

            # Node Redundancy Partner (0/RSP1/CPU0) is in STANDBY role
            p3_1 =  re.compile(r'\s*Node *Redundancy *Partner'
                                ' *\((?P<node>[a-zA-Z0-9\/]+)\) *is *in'
                                ' *(?P<role>[a-zA-Z]+) *role$')
            m = p3_1.match(line)
            if m:
                if 'standby' in str(m.groupdict()['role']).lower():
                    redundancy_dict['node'][node]['standby_node'] = str(m.groupdict()['node'])
                continue

            # Process Redundancy Partner (0/RSP0/CPU0) is in BACKUP role
            p3_3 =  re.compile(r'\s*Process *Redundancy *Partner'
                                ' *\((?P<node>[a-zA-Z0-9\/]+)\) *is *in'
                                ' *(?P<role>[a-zA-Z]+) *role$')
            m = p3_3.match(line)
            if m:
                if 'backup' in str(m.groupdict()['role']).lower():
                    redundancy_dict['node'][node]['backup_process'] = str(m.groupdict()['node'])
                continue

            # Standby node in 0/RSP1/CPU0 is ready
            # Standby node in 0/RSP1/CPU0 is NSR-ready
            p3_2 = re.compile(r'\s*Standby *node *in *([a-zA-Z0-9\/]+)'
                               ' *is *(?P<ready>[a-zA-Z\-]+)$')
            m = p3_2.match(line)
            if m:
                redundancy_dict['node'][node]['ready'] = \
                    str(m.groupdict()['ready'])
                continue

            # Node 0/RP0/CPU0 has no valid partner
            p3 = re.compile(r'\s*Node +([a-zA-Z0-9\/]+) +has +(?P<valid_partner>\S+)'
                             ' +valid +partner$')
            m = p3.match(line)
            if m:
                redundancy_dict['node'][node]['valid_partner'] = \
                str(m.groupdict()['valid_partner'])
                continue

            # v6-routing       0/RSP0/CPU0     N/A             Not Ready
            p4 = re.compile(r'\s*(?P<group>[a-zA-Z0-9\-]+)'
                             ' +(?P<primary>[A-Z0-9\/]+)'
                             ' +(?P<backup>[A-Z0-9\/]+)'
                             ' +(?P<status>[a-zA-Z\-\s]+)$')
            m = p4.match(line)
            if m:
                if 'group' not in redundancy_dict['node'][node]:
                    redundancy_dict['node'][node]['group'] = {}

                group = str(m.groupdict()['group'])
                if group not in redundancy_dict['node'][node]['group']:
                    redundancy_dict['node'][node]['group'][group] = {}
                    redundancy_dict['node'][node]['group'][group]['primary'] = \
                        str(m.groupdict()['primary'])
                    redundancy_dict['node'][node]['group'][group]['backup'] = \
                        str(m.groupdict()['backup'])
                    redundancy_dict['node'][node]['group'][group]['status'] = \
                        str(m.groupdict()['status'])
                    continue

            # NSR not ready since Backup is not Present
            p5 = re.compile(r'\s*NSR +(?P<primary_rmf_state>[a-zA-Z\s]+) +since'
                             ' +(?P<primary_rmf_state_reason>[a-zA-Z\s]+)$')
            m = p5.match(line)
            if m:
                redundancy_dict['node'][node]['primary_rmf_state'] = \
                    str(m.groupdict()['primary_rmf_state'])
                redundancy_dict['node'][node]\
                    ['primary_rmf_state_reason'] = \
                    str(m.groupdict()['primary_rmf_state_reason'])
                continue

            # A9K-RSP440-TR reloaded Thu Apr 27 02:14:12 2017: 1 hour, 16 minutes ago
            p6 = re.compile(r'\s*(?P<node_name>[a-zA-Z0-9\-]+) +reloaded'
                             ' +(?P<last_reload_timestamp>[a-zA-Z0-9\:\s]+):'
                             ' +(?P<time_since_last_reload>[a-zA-Z0-9\,\s]+)$')
            m = p6.match(line)
            if m:
                redundancy_dict['node'][node]['last_reload_timestamp'] =\
                    str(m.groupdict()['last_reload_timestamp'])
                redundancy_dict['node'][node]['time_since_last_reload'] =\
                    str(m.groupdict()['time_since_last_reload'])
                continue

            # Active node booted Thu Apr 27 03:22:37 2017: 8 minutes ago
            # Active node booted Thu Jan 11 12:31:59 2018: 5 days, 23 hours,  ago
            # Active node booted Tue Jan  2 07:32:33 2018: 1 day, 1 hour, 6 minutes ago
            # Active node booted Thu Jan 11 12:32:03 2018: 1 week, 4 days, 20 hours, 19 minutes ago
            p7 = re.compile(r'\s*Active +node +booted'
                            ' +(?P<node_uptime_timestamp>[a-zA-Z0-9\:\s]+):'
                            ' +(?P<node_uptime>((?P<ignore>\d+ \w+, *)?((?P<week>\d+) +(week|weeks), )?'
                            '(((?P<day>\d+) +(day|days))?, )?)?(((?P<hour>\d+) +(hour|hours))?, )?'
                            '(((?P<minute>\d+) +(minute|minutes))|((?P<second>\d+) +(seconds|seconds)))?) +ago$')
            m = p7.match(line)
            if m:
                redundancy_dict['node'][node]['node_uptime_timestamp'] = \
                    str(m.groupdict()['node_uptime_timestamp'])
                redundancy_dict['node'][node]['node_uptime'] = \
                    str(m.groupdict()['node_uptime'])
                time_in_seconds = 0
                if m.groupdict()['week']:
                    time_in_seconds += int(m.groupdict()['week']) * 7 * 86400
                if m.groupdict()['day']:
                    time_in_seconds += int(m.groupdict()['day']) * 86400
                if m.groupdict()['hour']:
                    time_in_seconds += int(m.groupdict()['hour']) * 3600
                if m.groupdict()['minute']:
                    time_in_seconds += int(m.groupdict()['minute']) * 60
                if m.groupdict()['second']:
                    time_in_seconds += int(m.groupdict()['second'])
                redundancy_dict['node'][node]['node_uptime_in_seconds'] = \
                    time_in_seconds
                continue

            # Standby node boot Thu Aug 10 08:29:18 2017: 1 day, 32 minutes ago
            p7_1 = re.compile(r'\s*Standby +node +boot'
                               ' +(?P<standby_node_timestamp>[a-zA-Z0-9\:\s]+):'
                               ' +(?P<time_since_standby_boot>[a-zA-Z0-9\,\s]+)$')
            m = p7_1.match(line)
            if m:
                standby_node_timestamp = str(m.groupdict()['standby_node_timestamp'])
                time_since_standby_boot = str(m.groupdict()['time_since_standby_boot'])

                redundancy_dict['node'][node]['standby_node_timestamp'] = \
                standby_node_timestamp
                redundancy_dict['node'][node]['time_since_standby_boot'] = \
                time_since_standby_boot
                continue

            # Standby node last went not ready Fri Aug 11 07:13:26 2017: 1 hour, 48 minutes ago
            # Standby node last went ready Fri Aug 11 07:13:26 2017: 1 hour, 48 minutes ago

            p7_2 = re.compile(r'\s*Standby *node *last *went *not *ready'
                               ' *(?P<standby_node_not_ready>[a-zA-Z0-9\:\s]+):'
                               ' *(?P<time_since_standby_node_not_ready>[a-zA-Z0-9\,\s]+)$')
            m = p7_2.match(line)
            if m:
                standby_node_not_ready = str(m.groupdict()['standby_node_not_ready'])
                time_since_standby_node_not_ready = str(m.groupdict()['time_since_standby_node_not_ready'])

                redundancy_dict['node'][node]['standby_node_not_ready'] = \
                standby_node_not_ready
                redundancy_dict['node'][node]['time_since_standby_node_not_ready'] = \
                time_since_standby_node_not_ready
                continue

            p7_3 = re.compile(r'\s*Standby *node *last *went *ready'
                               ' *(?P<standby_node_ready>[a-zA-Z0-9\:\s]+):'
                               ' *(?P<time_since_standby_node_ready>[a-zA-Z0-9\,\s]+)$')
            m = p7_3.match(line)
            if m:
                standby_node_ready = str(m.groupdict()['standby_node_ready'])
                time_since_standby_node_ready = str(m.groupdict()['time_since_standby_node_ready'])

                redundancy_dict['node'][node]['standby_node_ready'] = \
                standby_node_ready
                redundancy_dict['node'][node]['time_since_standby_node_ready'] = \
                time_since_standby_node_ready
                continue

            # Last switch-over Thu Apr 27 03:29:57 2017: 1 minute ago
            p8 = re.compile(r'\s*Last +switch-over'
                        ' +(?P<last_switchover_timepstamp>[a-zA-Z0-9\:\s]+):'
                        ' +(?P<time_since_last_switchover>[a-zA-Z0-9\,\s]+)$')
            m = p8.match(line)
            if m:
                redundancy_dict['node'][node]['last_switchover_timepstamp'] = \
                    str(m.groupdict()['last_switchover_timepstamp'])
                redundancy_dict['node'][node]['time_since_last_switchover'] = \
                    str(m.groupdict()['time_since_last_switchover'])
                continue

            # Active node reload  Cause: Initiating switch-over.
            p9 = re.compile(r'\s*Active +node +reload *(?:Cause)?:'
                             ' +(?P<reload_cause>[a-zA-Z\-\s]+).$')
            m = p9.match(line)
            if m:
                redundancy_dict['node'][node]['reload_cause'] = \
                    str(m.groupdict()['reload_cause'])
                continue

        return redundancy_dict