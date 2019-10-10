import re
from subprocess import Popen, PIPE

class AsteriskCli(object):

    def __init__(self):
        pass

    def execute_cli(self, cmd):
        process = Popen(["asterisk", "-rx", cmd], stdout=PIPE)
        (output, err) = process.communicate()
        exit_code = process.wait()

        if exit_code != 0:
            raise Exception("asterisk console returned %i, output is %s" % (exit_code, output))

        return output

    def parse_channels(self, output):

        lines = output.splitlines()

        chans = []
        for line in lines:

            values = line.split('!')
            chan = {
                'name': values[0],
                'context': values[1],
                'exten': values[2],
                'priority': int(values[3]),
                'state': values[4],
                'application': values[5],
                'data': values[6],
                'caller_number': values[7],
                'accountcode': values[8],
                'peeraccount': values[9],
                'amaflags': int(values[10]),
                'duration': values[11],
                'bridgeid': values[12],
                'uniqueid': values[13],
            }
            chans.append(chan)
        return chans

    def parse_channel_stats(self, output):

        lines = output.splitlines()
        # skip header lines
        lines = lines[5:]

        chans = []
        for line in lines:

            # footer?
            if line == '' or (' not valid' in line) or 'Objects found: ' in line:
                continue

            # the first 9 is actually 8, but includes the first space
            values = self._parse_line(line, [9, 18, 8, 6, 7, 7, 3, 7, 7, 7, 3, 7, 7])
            chan = {
                'bridgeid': self._parse_string(values[0]),
                'channelid': self._parse_string(values[1]),
                'uptime': values[2],
                'codec': self._parse_string(values[3]),
                'rx_count': self._parse_int_with_suffix(values[4]),
                'rx_lost': self._parse_int_with_suffix(values[5]),
                'rx_pct': self._parse_int(values[6]),
                'rx_jitter': self._parse_float(values[7]),
                'tx_count': self._parse_int_with_suffix(values[8]),
                'tx_lost': self._parse_int_with_suffix(values[9]),
                'tx_pct': self._parse_int(values[10]),
                'tx_jitter': self._parse_float(values[11]),
                'rtt': self._parse_float(values[12]),
            }
            chans.append(chan)
        return chans

    def parse_taskprocessors(self, output):

        lines = output.splitlines()
        # skip header lines
        lines = lines[2:]
        # skip footer lines
        lines = lines[:-3]

        processors = []
        for line in lines:
            # in most cases the output is fixed-width columns, but if numbers get higher (10M+), the layout gets variable
            word = '([^\\s]+)'
            space = '[\\s]+'
            regexp = word + space + word + space + word + space + word + space + word + space + word
            matches = re.search(regexp, line)
            entry = {
                'name': self._parse_string(matches.group(1)),
                'processed': self._parse_int(matches.group(2)),
                'in_queue': self._parse_int(matches.group(3)),
                'max_depth': self._parse_int(matches.group(4)),
                'low_water': self._parse_int(matches.group(5)),
                'high_water': self._parse_int(matches.group(6)),
            }
            processors.append(entry)
        return processors

    def get_channels(self):
        out = self.execute_cli('core show channels concise')
        return self.parse_channels(out)

    def get_channel_stats(self):
        out = self.execute_cli('pjsip show channelstats')
        return self.parse_channel_stats(out)

    def get_channel_stats_test(self):
        f = open('/home/nathan/Desktop/sampleoutput.txt', 'r')
        c = f.read()
        return self.parse_channel_stats(c)

    def get_taskprocessors(self):
        out = self.execute_cli('core show taskprocessors')
        return self.parse_taskprocessors(out)

    # privates

    # parse a line with space-separated fields with fixes lengths
    def _parse_line(self, line, lens):
        idx = 0
        fields = []
        for len in lens:
            fields.append(line[idx:idx+len])
            idx = idx + len + 1
        return fields

    def _parse_string(self, val):
        return val.strip()

    def _parse_int(self, val):
        return int(val)

    def _parse_float(self, val):
        return float(val)

    def _parse_int_with_suffix(self, val):
        suffix = val[-1:]
        if suffix == 'K':
            multiplier = 1000
        elif suffix == ' ':
            multiplier = 1
        else:
            raise Exception("Unknown multiplier %s" % suffix)

        return int(val[0:-1]) * multiplier
