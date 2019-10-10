#!/usr/bin/env python2

import os
from AsteriskCli import AsteriskCli
from subprocess import Popen, PIPE
from munin import MuninPlugin

class AsteriskTaskProcessors(MuninPlugin):
    args = "-l 0 -u 100"
    vlabel = "percent"
    scale = False
    category = "asterisk"

    def __init__(self):
        self.title = "Asterisk Task Processors"
        super(MuninPlugin, self).__init__()

    def autoconf(self):
        return True

    @property
    def fields(self):
        warning = os.environ.get('perc_warn', 50)
        critical = os.environ.get('perc_crit', 80)
        return [
            ("current_max", dict(
                label="Current max",
                info='The filled percentage of the currently fullest task processor queue',
                type="GAUGE",
                min="0",
                warning=str(warning),
                critical=str(critical))),
            ("overal_max", dict(
                            label="Overal max",
                            info='The filled percentage of the overal fullest task processor queue',
                            type="GAUGE",
                            min="0",
                            warning=str(warning),
                            critical=str(critical)))
        ]

    def execute(self):
        return self.get_stats()

    def get_stats(self):
        processors = AsteriskCli().get_taskprocessors()

        # parse
        max_current_val = 0
        max_overal_val = 0
        for processor in processors:

            current = (float(processor['in_queue']) / float(processor['high_water'])) * 100
            overal = (float(processor['max_depth']) / float(processor['high_water'])) * 100

            max_current_val = max(current, max_current_val)
            max_overal_val = max(overal, max_overal_val)

        return dict(current_max = max_current_val, overal_max = max_overal_val)

    def debug(self, str):
        print str
        pass

if __name__ == "__main__":
    AsteriskTaskProcessors().run()
