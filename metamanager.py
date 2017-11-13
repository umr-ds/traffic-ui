#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from collections import namedtuple
from flowfactory import flow, Flowfactory
from os import path
from time import sleep
from threading import Thread


''' This file contains the MetaManager-class which stores the flow's metadata
    like source and destination or the AS. It is also an extended Thread which
    checks for new pcaps.

    This file is also executable and creates the MetaData-cache file for each
    pcap in the specified 'input'-folder specified in the configuration.'''


'Storage for a flow\'s metadata.'
MetaFlow = namedtuple('MetaFlow',
  ['filename', 'hash', 'src_ip', 'src_port', 'dst_ip', 'dst_port',
   'asn', 'as_name', 'bgp_prefix'])


def flow_to_meta_flow(f):
    'Creates a MetaFlow based on a flowfactory.flow.'
    from socket import inet_ntoa

    if hasattr(f, 'asn'):
        (asn, as_name, bgp_prefix) = (f.asn, f.as_name, f.bgp_prefix)
    else:
        (asn, as_name, bgp_prefix) = (None, None, None)

    return MetaFlow(
      f._filename, f.hash,
      inet_ntoa(f.srcip), f.srcport,
      inet_ntoa(f.dstip), f.dstport,
      asn, as_name, bgp_prefix)


class MetaManager(Thread):
    'The MetaManager interacts with the Flowfactory to handle metadata.'

    def __init__(self, flowfactory, flow_store, sync=True, background=True):
        self.flowfactory = flowfactory
        self.flow_store = flow_store
        self.meta_store = {}
        self.meta_cache = '{}/meta_cache.csv'.format(flowfactory.cache_path)

        self._read_store()

        if sync and self.scan_flows() > 0:
            self._write_store()

        if background:
            Thread.__init__(self)
            self.name = 'MetaManager'

    def run(self):
        while True:
            if self.scan_flows() > 0:
                self._write_store()
            sleep(60)

    def _read_store(self):
        'Creates the meta_store from meta_cache.'
        if not path.isfile(self.meta_cache):
            open(self.meta_cache, 'a+').close()
            return

        with open(self.meta_cache, 'r') as store:
            reader = csv.reader(store)
            for l in reader:
                if l[6] == '':
                    (asn, as_name, bgp_prefix) = (None, None, None)
                else:
                    (asn, as_name, bgp_prefix) = (l[6], l[7], l[8])

                meta_flow = MetaFlow(
                  l[0], l[1], l[2], l[3], l[4], l[5], asn, as_name, bgp_prefix)
                self.meta_store.update({meta_flow.filename: meta_flow})

    def _write_store(self):
        'Writes the meta_store to the meta_cache.'
        with open(self.meta_cache, 'w+') as store:
            writer = csv.writer(store)
            for meta_flow in self.meta_store.values():
                writer.writerow(list(meta_flow))

    def scan_flows(self):
        '''Iterates over the pcap-store to acquire each flow\'s metadata
           and returns the amount of changed entries.'''
        changes = 0
        pcap_list = map(lambda f: '{}/{}'.format(self.flow_store, f),
          Flowfactory.flow_list(self.flow_store))

        for f in pcap_list:
            if f in self.meta_store and \
              Flowfactory.head_hash(f) == self.meta_store[f].hash:
                continue

            flow = self.flowfactory.get_flow(f)
            meta_flow = flow_to_meta_flow(flow)
            self.meta_store.update({meta_flow.filename: meta_flow})
            changes += 1

        for meta_flow in self.meta_store.keys():
            if meta_flow not in pcap_list:
                del self.meta_store[meta_flow]
                changes += 1

        return changes


if __name__ == '__main__':
    import argparse
    from traffic_ui import parse_config

    parser = argparse.ArgumentParser()
    parser.add_argument(
      '-c', '--config', help='path to config (default: ./config.ini)')
    args = parser.parse_args()

    if args.config is None and not path.isfile('./config.ini'):
        print('No config was found!\n' +
          'Please place a config.ini in your current working directory or ' +
          'supply a path by -c. If you\'re on a fresh instance, copy the ' +
          'config-example.ini to config.ini and modify your copy.')
        exit(1)

    conf = parse_config(
      args.config if args.config is not None else './config.ini')

    try:
        if not path.isdir(conf.cache):
            makedirs(conf.cache)
    except:
        print('The cache-directory does not exists and can not be created!')
        exit(1)

    import cymru
    cymru.DB_PATH = conf.cache + '/asn.db'

    flow_factory = Flowfactory(conf.cache, conf.store)

    meta_manager = MetaManager(flow_factory, conf.input, background=False)
