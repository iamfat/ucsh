# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import sys
from .options import Options
from .ucloud import UCloud
from .shell import Shell

def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        print ('usage: ucsh [command] [option ...]')
        sys.exit()

    options = Options()
    options.load()

    ucloud = UCloud(options)
    sh = Shell(ucloud=ucloud)
    if len(sys.argv) >= 2:
        sh.onecmd(' '.join(sys.argv[1:]))
    else:
        try:
            sh.cmdloop()
        except KeyboardInterrupt:
            print('')


if __name__ == "__main__":
    main()

