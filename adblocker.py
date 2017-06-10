#!/usr/bin/env python3

import os.path

from PyQt5 import QtWebEngineCore

authority_blacklist = []

# If a hosts file is supplied, we can use it as a simple ad blocking filter list.
if os.path.isfile("hosts"):
    with open("hosts") as fobject:
        lines = fobject.read().splitlines()
        for line in lines:
            # Ignore comments.
            if line.startswith("#"):
                continue
            url = line.split()
            if len(url) > 0:
                url = url[-1]
                authority_blacklist.append(url)
        del lines

class AdBlocker(QtWebEngineCore.QWebEngineUrlRequestInterceptor):
    """This is an ad-blocking request interceptor that can be assigned to QtWebEngine."""
    
    def interceptRequest(self, info):
        if info.requestUrl().authority() in authority_blacklist:
            info.block(True)
