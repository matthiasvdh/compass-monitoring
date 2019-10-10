#!/usr/bin/env python2

# Provides channel info like https://github.com/munin-monitoring/contrib/blob/master/plugins/asterisk/asterisk
# for Asterisk 15.

from AsteriskCli import AsteriskCli
from munin import MuninPlugin

# Display number of channels in Asterisk, grouped by their type.
class AsteriskChannels(MuninPlugin):
    args = "--base 1000 -l 0"
    vlabel = "channels"
    scale = False
    category = "asterisk"
    types = ['Local', 'PJSIP']
    printf = '%7.0lf'

    def __init__(self):
        self.title = "Asterisk Channels"
        super(MuninPlugin, self).__init__()

    def autoconf(self):
        return True

    @property
    def fields(self):
        fields = [('all', dict(
            label = 'all',
            draw = 'LINE',
            type = 'GAUGE',
            min = 0
        ))]
        first = True
        for type in self.types:
            opts = dict(
                label = type,
                draw = 'AREA' if first else 'STACK',
                type = "GAUGE",
                min = "0"
            )
            first = False
            fields.append( (type, opts ))
        return fields

    def execute(self):
        return self.get_stats()

    def get_stats(self):

        cli = AsteriskCli()

        values = {'all': 0}
        for type in self.types:
            values[type] = 0

        for chan in cli.get_channels():
            values['all'] = values['all'] + 1
            type = chan['name'].split('/')[0]
            if type in values:
                values[type] = values[type] + 1

        return values

    def debug(self, str):
        print str
        pass

if __name__ == "__main__":
    AsteriskChannels().run()
