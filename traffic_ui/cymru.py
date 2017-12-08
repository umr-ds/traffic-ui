#!/usr/bin/env python
# wrapper for team-cymru.org ip lookups
from __future__ import print_function
import socket, csv, os.path, sys, netaddr
from netaddr import IPNetwork, IPAddress

BUFFER_SIZE = 65535
debug = False

def eprint(*args, **kwargs):
    if debug or kwargs.pop('force', False):
        print(*args, file=sys.stderr, **kwargs)

DB_PATH = os.path.dirname(os.path.realpath(__file__))+"/asn.db"
eprint("Using database at {}".format(DB_PATH))

db = []

def _query_whois(ip):
    ADDRESS = ("whois.cymru.com", 43)
    ADDRESS = ("38.229.36.110", 43)
    ADDRESS = ("38.229.36.111", 43)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(ADDRESS)
    s.send("-v {}\n".format(ip))
    data = s.recv(BUFFER_SIZE).split("\n")
    s.close()
    return data[:2]

def whois_dict(ip):
    """lookup an asn entry using a whois request"""
    try: data = _query_whois(ip)
    except socket.error: return {}
    keys = [key.strip() for key in data[0].split("|")]
    values = [value.strip() for value in data[1].split("|")]
    return dict(zip(keys, values))

def local_lookup(ip):
    """lookup an asn entry in the local database"""
    for entry in db:
        if entry["IP"] == ip:
            eprint("Matched IP in database")
            return entry
        try:
            if IPAddress(ip) in IPNetwork(entry["BGP Prefix"]):
                eprint("Matched BGP CIDR Network in database")
                return entry
        except netaddr.core.AddrFormatError:
            pass
    eprint("No match in database.")

def lookup(ip):
    """lookup an asn entry by first checking the local db, and if needed by using whois"""
    if os.path.isfile(DB_PATH):
        csvfile = open(DB_PATH, "r")
        global db
        db = list(csv.DictReader(csvfile))

    local = local_lookup(ip)
    if local:
        eprint("# Found local entry.")
        return local

    response = whois_dict(ip)
    try:
        if response["IP"] == ip:
            eprint("# Did succesful whois query.")
    except KeyError:
        eprint("# Whois query failed. {}".format("".join(response)), force=True)
        return

    if os.path.isfile(DB_PATH):
        eprint("# Writing to existing DB")
        csvfile = open(DB_PATH, "a")
        new_db = csv.writer(csvfile)
        values = [response[k] for k in db[0].keys()]
        new_db.writerow(values)
    else:
        eprint("# Creating DB")
        csvfile = open(DB_PATH, "w")
        new_db = csv.writer(csvfile)
        new_db.writerow(response.keys())
        new_db.writerow(response.values())

    return response

if __name__=="__main__":
    from pprint import pprint
    pprint(lookup(sys.argv[1]))
