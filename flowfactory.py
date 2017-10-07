#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flowinspector import flow as fi_flow
from pickle import dump as pickle, load as unpickle
from os import listdir, path, remove

class flow(fi_flow):
    'Overload the original flow for ratings and stuff'

    def __init__(self, filename, ratings=[]):
        fi_flow.__init__(self, filename)
        # user-ratings for the traffic-ui
        self.ratings = ratings
        # set ASN
        self.lookupASN()
        self.hash = Flowfactory.head_hash(filename)

class Flowfactory:
    'A class to store cached versions of flows and auto-load them.'

    def __init__(self, cache_path):
        self.cache_path = cache_path

    @staticmethod
    def pickle_name(filename):
        'Returns a relative pickled filename from the given pcap.'
        from re import sub
        return sub('.pcap$', '.pickle', path.basename(filename))

    def find_pickle(self, filename):
        'Tries to find a pickled filename (or None) for the given filename.'
        files = filter(
          lambda f: f == self.pickle_name(filename), listdir(self.cache_path))
        return files[0] if files else None
        
    def get_flow(self, filename):
        '''Returns a flow for the given filename from the original file or the
           cached file and creates a cache file if it doesn't exists yet.'''
        has_pickle = self.find_pickle(filename)
        pickle_file = self.cache_path + '/' + self.pickle_name(filename)

        if not has_pickle:
            # Read file and save cached file
            ret_flow = flow(filename)
            with open(pickle_file, 'w+') as out_file:
                pickle(ret_flow, out_file)
        else:
            # Restore file from cache
            with open(pickle_file, 'r') as in_file:
                ret_flow = unpickle(in_file)

            if ret_flow.hash != Flowfactory.head_hash(filename):
                print('{} has changed, rehashing!'.format(filename))
                remove(pickle_file)
                return self.get_flow(filename)

        return ret_flow

    @staticmethod
    def head_hash(filename):
        'Caluclate a hash for the head of a file'
        from hashlib import sha1

        sha1_hash = sha1()
        with open(filename, 'r') as in_file:
            count = 32
            buf = in_file.read(65536)
            while len(buf) > 0 and count > 0:
                sha1_hash.update(buf)
                buf = in_file.read(65536)
                count -= 1
        return sha1_hash.hexdigest()
