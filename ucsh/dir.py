# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)
__metaclass__ = type

import sys

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
levels = [ None, 'region', 'resource_type', 'resource']

class Dir(object):

    level = None
    path = []

    def __init__(self, path='', ucloud=None):
        self.ucloud = ucloud
        self.path = path.strip('/').split('/')
        self.autofix()

    def autofix(self):
        l = len(self.path)
        if l>0 and self.path[0] not in regions.keys():
            del self.path[0:]
        if l>1 and self.path[1] not in resource_types:
            del self.path[1:]
        if l>2:
            if self.path[1] =='hosts':
                if self.path[2] not in self.hosts(self.path[0]):
                    del self.path[2:]
            else:
                del self.path[2:]
        self.level = levels[len(self.path)]
        return True

    def chdir(self, path):
        if path == '..':
            del self.path[-1:]
        elif len(path) > 0:
            path = path.strip('/')
            if len(path)>0:
                self.path.extend(path.split('/'))
        else:
            return
        self.autofix()

    def files(self,detail=False):
        if detail:
            if self.level == 'region':
                return resource_types
            elif self.level == 'resource_type':
                if self.path[1] == 'hosts':
                    return self.hosts(region=self.path[0],detail=detail)
            elif self.level == 'resource':
                return []
            return regions
        else:
            if self.level == 'region':
                return resource_types
            elif self.level == 'resource_type':
                if self.path[1] == 'hosts':
                    return self.hosts(region=self.path[0])
            elif self.level == 'resource':
                return []
            return regions.keys()

    def hosts(self, region, detail=False):
        resp = self.ucloud.DescribeUHostInstance(Region=region)
        if resp['RetCode'] == 0:
            if detail:
                return resp['UHostSet']
            else:
                return map(lambda h: h['Name'], resp['UHostSet'])
        else:
            print("[{code}] {message}".format(code=resp['RetCode'],
                message=resp['Message']), file=sys.stderr)
        return []

    def host(self):
        if self.level == 'resource' and self.path[1] == 'hosts':
            resp = self.ucloud.DescribeUHostInstance(Region=self.path[0])
            if resp['RetCode'] == 0:
                return filter(lambda h: h['Name'] == self.path[2], resp['UHostSet'])[0]
        return None

    def __str__(self):
        return '/'.join(self.path)

