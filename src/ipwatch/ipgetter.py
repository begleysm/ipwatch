"""
This module is designed to fetch your external IP address from the internet.
It is used mostly when behind a NAT.
It picks your IP randomly from a serverlist to minimize request
overhead on a single server


API Usage
=========

    >>> import ipgetter
    >>> myip = ipgetter.myip()
    >>> myip
    '8.8.8.8'

    >>> ipgetter.IPgetter().test()

    Number of servers: 47
    IP's :
    8.8.8.8 = 47 ocurrencies


Copyright 2014 phoemur@gmail.com
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

Updated by Sean Begley for the ipwatch project (https://github.com/begleysm/ipwatch/)
"""

import http.cookiejar as cjar
import json
import os
import random
import re
import socket
import ssl
import urllib.request as urllib
from datetime import datetime, timedelta

import platformdirs

__version__ = "0.7"

def myip():
    return IPgetter().get_ips()

SERVERLIST_URL = "https://raw.githubusercontent.com/begleysm/ipwatch/master/servers.json"

class IPgetter:
    """
    This class is designed to fetch your external IP address from the internet.
    It is used mostly when behind a NAT.
    It picks your IP randomly from a serverlist to minimize request overhead
    on a single server
    """

    def __init__(self, serverlist_file = None):
        servercache_file = platformdirs.user_cache_path() / "serverCache.json"
        now = datetime.now()
        current_ts = datetime.timestamp(now)
        self.serverlist = self.get_serverlist(serverlist_file)

    def get_serverlist(serverlist_file = None)
        server_list = None
        if os.path.isfile(servercache_file):
            try:
                with open(servercache_file) as infile:
                    server_list = json.load(infile)
            except:
                pass

        if (
            server_list is None
            or "expiry" not in server_list
            or "expiryDisplay" not in server_list
            or "servers" not in server_list
            or server_list["expiry"] is None
            or server_list["expiryDisplay"] is None
            or server_list["servers"] is None
            or not isinstance(server_list["expiry"], float)
            or len(str(server_list["expiry"])) == 0
            or not isinstance(server_list["servers"], list)
            or len(server_list["servers"]) == 0
            or server_list["expiry"] < current_ts
        ):  # we will go off and get the list again
            expiry_date = now + timedelta(days=90)
            server_list = {
                "expiry" : datetime.timestamp(expiry_date),
                "expiryDisplay" : expiry_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "servers" : [],
            }

            f = urllib.urlopen(SERVERLIST_URL)

            if f.getcode() == 200:
                data = f.read().decode("utf-8")
                server_list["servers"] = json.loads(data)
                with open(servercache_file, "w") as outfile:
                    outfile.write(json.dumps(server_list, indent=4))
            else:
                raise urllib.error.HTTPError("Error receiving data", f.getcode())

        return server_list["servers"]

    def get_externalip(self):
        """
        This function gets your IP from a random server
        """

        myip = ""
        for _ in range(7):
            server = random.choice(self.server_list)
            myip = self.fetch(server)
            if myip != "":
                break
        return myip, server

    def get_local_ip(self):
        # From https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def get_ips(self):
        local_ip = self.get_local_ip()
        external_ip, server = self.get_externalip()
        return external_ip, local_ip, server

    def fetch(self, server):
        """
        This function gets your IP from a specific server.
        """
        url = None
        cj = cjar.CookieJar()
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        opener = urllib.build_opener(
            urllib.HTTPCookieProcessor(cj), urllib.HTTPSHandler(context=ctx)
        )
        opener.addheaders = [
            (
                "User-agent",
                "Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0",
            ),
            (
                "Accept",
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            ),
            ("Accept-Language", "en-US,en;q=0.5"),
        ]

        try:
            url = opener.open(server, timeout=4)
            content = url.read()

            # Didn't want to import chardet. Prefered to stick to stdlib
            try:
                content = content.decode("UTF-8")
            except UnicodeDecodeError:
                content = content.decode("ISO-8859-1")

            m = re.search(
                r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
                content,
            )
            myip = m.group(0)
            return myip if len(myip) > 0 else ""
        except Exception:
            return ""
        finally:
            if url:
                url.close()

    def test(self):
        """
        This functions tests the consistency of the servers
        on the list when retrieving your IP.
        All results should be the same.
        """

        from collections import Counter

        resultdict = {
            server : self.fetch(server)
            for server in self.server_list
        }

        print("Number of servers: ", len(self.server_list))
        print("IP's :", Counter(resultdict.values()))
        print("Full result: ", resultdict)

        valid_ips = set(r for r in resultdict.values() if r != '')
        assert(len(valid_ips) >= 1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help ="tests the consistency of the servers")

    args = parser.parse_args()
    if args.verify:
        IPgetter().test()
    else:
        print(myip())
