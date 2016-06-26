# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
__metaclass__ = type

import sys, os
from cmd import Cmd
from tabulate import tabulate
from .ucloud import UCloud
from .dir import Dir

import readline
import yaml

if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

# 确保tab操作的时候 '-', '/' 能够被正确的识别
old_delims = readline.get_completer_delims()
readline.set_completer_delims(old_delims.replace('-', '').replace('/', ''))

class Shell(Cmd):
    intro = '\x1b[1mUCLOUD SHELL\x1b[0m by \x1b[1;3mJia Huang\x1b[0m <\x1b[4miamfat@gmail.com\x1b[0m>. Type help or ? to list commands.\n'
    
    prompt_prefix = '\x1b[1;34mUCLOUD\x1b[0m '
    prompt_suffix = '$ '

    file = None

    def __init__(self, completekey='tab', stdin=None, stdout=None, ucloud=None):
        Cmd.__init__(self, completekey, stdin, stdout)
        self.ucloud = ucloud
        self.dir = Dir(ucloud=ucloud)
        self.update_prompt()

    def update_prompt(self):
        self.prompt = ''.join([
            self.prompt_prefix, str(self.dir), self.prompt_suffix])

    def precmd(self, line):
        line = line.lower()
        if self.file and 'playback' not in line:
            print(line, file=self.file)
        return line
 
    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def complete_cd(self, text, line, begidx, endidx):
        self_start = str(self.dir)
        d = Dir(path=self_start,ucloud=self.ucloud)
        d.chdir(text)
        start = str(d).replace(self_start, '').strip('/')
        t = text.replace(start, '').strip('/')
        return map(lambda v: (start + '/' + v) if len(start)>0 else v, 
                    filter(lambda v: v.startswith(t), d.files()))

    def do_exit(self, arg):
        self.close()
        return True

    def do_ls(self, arg):
        files = self.dir.files(detail=True)
        level = self.dir.level
        if level==None:
            print(tabulate(map(lambda k,v: [k, v], 
                files.keys(), files.values()), headers=[
                    'NAME', 'TITLE'
                ]))
            print("")
            return
        elif level=='resource_type':
            if self.dir.path[1] == 'hosts':
                print(tabulate(map(lambda name,ip,state: [name, ip, state],
                    map(lambda v:v['Name'], files), 
                    map(lambda v:v['IPSet'][0]['IP'], files),
                    map(lambda v:v['State'], files)
                ), headers=[
                    'NAME', 'IP', 'STATE'
                ]))
                print("")
                return
        print('\t'.join(files))

    def do_clear(self, arg):
        print('\033[2J\033[1;1H', end="")

    def do_cd(self, arg):
        self.dir.chdir(arg)
        self.update_prompt()

    def do_ssh(self, arg):
        host = self.dir.host()
        ip = host['IPSet'][0]['IP']
        os.system('ssh -A ' + ip)

    def do_info(self, arg):
        host = self.dir.host()
        print(yaml.safe_dump(host))

    def do_state(self, arg):
        host = self.dir.host()
        print(host['State'])