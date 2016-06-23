# -*- coding: utf-8 -*-
import os
from ConfigParser import ConfigParser

class Options(ConfigParser):
    """Parse and save options."""
    conf_path = os.path.expanduser('~/.ucloudrc')
    default_section = 'ucloud'
    default_value = ''

    def __getattr__(self, item):
        if self.has_option(self.default_section, item):
            return self.get(self.default_section, item)
        return self.default_value

    def save(self, **kwargs):
        for key, value in kwargs.items():
            self.set(self.default_section, key, value)

        with open(self.conf_path, 'wb') as f:
            self.write(f)

    def load(self):
        if not os.path.exists(self.conf_path):
            print("Sorry but I can't find the config file. Please fill the "
                  "following template and save it to %s" % self.conf_path)
            print("""
[ucloud]
public_key=
private_key=
base_url=https://api.ucloud.cn
""")
            sys.exit(2)
        with open(self.conf_path, 'r') as f:
            self.readfp(f)
