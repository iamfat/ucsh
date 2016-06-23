# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
__metaclass__ = type

import cmd
from tabulate import tabulate
from .ucloud import UCloud
import readline

regions = {
    'cn-north-01': '北京BGP-A', 
    'cn-north-02': '北京BGP-B', 
    'cn-north-03': '北京BGP-C', 
    'cn-north-04': '北京BGP-D',
    'cn-east-01': '华东双线', 
    'cn-east-02': '金融云', 
    'cn-south-01': '华南双线', 
    'cn-south-02': '广州BGP', 
    'hk-01': '亚太', 
    'us-west-01': '北美'
    }

resource_types = ['hosts']

levels = ['regions', 'resources']

# 确保tab操作的时候 '-', '/' 能够被正确的识别
old_delims = readline.get_completer_delims()
readline.set_completer_delims(old_delims.replace('-', '').replace('/', ''))

class Shell(cmd.Cmd):
    intro = '\x1b[1mUCLOUD SHELL\x1b[0m by \x1b[1;3mJia Huang\x1b[0m <\x1b[4miamfat@gmail.com\x1b[0m>. Type help or ? to list commands.\n'
    
    prompt_prefix = '\x1b[1;34mUCLOUD\x1b[0m '
    prompt_suffix = '$ '
    prompt = prompt_prefix + prompt_suffix
    file = None

    ucloud = None
    cwd = ''
    level = ''
    region = ''
    resource_type = ''
    resource = ''

    def update(self):
        args = self.cwd.split('/')
        self.level = ''

        if len(args) >= 1 and args[0]:
            self.level = 'region'
            self.region = args[0]

        if len(args) >= 2:
            self.level = 'resource_type'
            self.resource_type = args[1]

        if len(args) >= 3:
            self.level = 'resource'
            self.resource = args[2]

        self.prompt = ''.join([
            self.prompt_prefix, self.cwd, self.prompt_suffix])

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
        t = text.split('/')
        if len(t) == 1:
            return filter(lambda v: v.startswith(t[0]), regions)
        elif len(t) == 2:
            return map(lambda r: '/'.join([t[0],r]), 
                filter(lambda v: v.startswith(t[1]), resource_types))
        else:
            if t[1] == 'hosts':
                resp = self.ucloud.DescribeUHostInstance(Region=t[0])
                if resp['RetCode'] == 0:
                    return map(lambda h: '/'.join([t[0], t[1], h['Name']]),
                        resp['UHostSet'])

    def do_exit(self, arg):
        self.close()
        return True

    def do_ls(self, arg):
        if self.level == 'region':
            print('\t'.join(resource_types))

        elif self.level == 'resource_type':
            if self.resource_type == 'hosts':
                resp = self.ucloud.DescribeUHostInstance(Region=self.region)
                if resp['RetCode'] == 0:
                    print('\t'.join(map(lambda h: h['Name'],
                            resp['UHostSet'])))
                else:
                    print("[{code}] {message}".format(code=resp['RetCode'], message=resp['Message']))
            else:
                print('TBA')

        elif self.level == 'resource':
            print('TBA')

        else:
            print(tabulate(map(lambda k,v: [k, v], regions.keys(), regions.values()), headers=[u'REGION ID', u'REGION NAME']))
            print("")

    # def do_ssh(self, arg):
        # ssh

    def do_cd(self, arg):
        if arg == '/':
            self.cwd = ''
        elif arg == '..':
            parts = self.cwd.split('/')
            parts.pop()
            self.cwd = '/'.join(parts)
        elif arg == '.' or len(arg) == 0:
            # do nothing
            self.cwd
        else:
            arg = arg.strip(' \t\n\r./')
            if self.cwd:
                self.cwd += '/' + arg
            else:
                self.cwd = arg

        self.update()
