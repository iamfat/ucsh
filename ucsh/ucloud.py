# -*- coding: utf-8 -*-
import json
import contextlib
import hashlib
import urllib, urllib2

class UCloudAction:
    cached_responses = {}

    """UCloud API Action Helper."""
    def __init__(self, options, action):
        self.options = options
        self.action = action

    def __call__(self, **kwargs):
        params = dict(
            PublicKey=self.options.public_key, 
            Action=self.action, ProjectId=self.options.project_id)
        params.update(kwargs)
        self.sign(params)
        return self.request(params)

    def request(self, params):
        # cache any results
        url = self.options.base_url + '?' + urllib.urlencode(params)
        if url not in UCloudAction.cached_responses:
            with contextlib.closing(urllib2.urlopen(url)) as r:
                resp = r.read()
                resp = json.loads(resp)
                if resp['RetCode'] == 0:
                    UCloudAction.cached_responses[url] = resp
        return UCloudAction.cached_responses[url]

    def sign(self, params):
        private_key = self.options.private_key
        sign_str = ''.join(key+params[key] for key in sorted(params.keys()))
        sign_str += private_key
        params['Signature'] = hashlib.sha1(sign_str).hexdigest()

class UCloud:
    """UCloud API Client."""

    def __init__(self, options):
        self.options = options

    def __getattr__(self, action):
        return UCloudAction(self.options, action)

