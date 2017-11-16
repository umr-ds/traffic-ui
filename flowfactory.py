#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from collections import namedtuple
from flowinspector import flow as fi_flow
from os import listdir, path, remove
from pickle import dump as pickle, load as unpickle

'Storeage for csv-entries in the store_filename.'
CSVRow = namedtuple('CSVRow', ['filename', 'hash', 'ratings'])


def csv_row_to_list(csvrow):
    'Converts a CSVRow to a simple list.'
    return [csvrow.filename, csvrow.hash] + csvrow.ratings


class flow(fi_flow):
    '''Overload the original flow for interaction with the Flowfactory,
       extra fields and stuff'''

    def __init__(self, filename, ratings=[]):
        fi_flow.__init__(self, filename)

        self.ratings = ratings

        self.lookupASN()
        self.hash = Flowfactory.head_hash(filename)

    def plot_png_data(self, plot_path):
        '''Reads a PNG-image from a plot_path and returns a base64-encoded
           HTML-image-tag.'''
        from base64 import b64encode

        with open(plot_path, 'r') as inpt:
            plot_raw = inpt.read()

        return '<img class="pure-img" src="data:image/png;base64,{}" />'.format(
          b64encode(plot_raw))

    def plot_data(self, flow_factory, backend):
        '''Saves or fetches a plot to a cache observed by a Flowfactory and
           returns the HTML-version of the plot.'''
        if backend not in flow_factory.plot_backends:
            raise Exception('Unknown plot-backend specified.')

        plot_path = flow_factory.cache_path + "/" + \
          Flowfactory.pickle_name(self._filename, ext='.{}'.format(backend))

        if not path.isfile(plot_path):
            # This list must be synchronized with Flowfactory.plot_backends!
            if backend == 'plotly':
                from plotly.offline import plot
                from plotly.tools import mpl_to_plotly
    
                plt = self.show(show=False)
                plt.tight_layout()
    
                plotly_fig = mpl_to_plotly(plt.gcf())
                plotly_fig['layout']['showlegend'] = True;
    
                plot_div = plot(plotly_fig,
                  show_link=False, output_type='div', include_plotlyjs=False)
    
                with open(plot_path, 'w') as outpt:
                    outpt.write(plot_div)
                    outpt.close()

            elif backend == 'png':
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                plt.rcParams['figure.figsize'] = (9, 7)

                plot = self.show(show=False)
                plot.savefig(plot_path, format='png')
                plot.close()

                plot_div = self.plot_png_data(plot_path)

        else:
            if backend == 'plotly':
                with open(plot_path, 'r') as inpt:
                    plot_div = inpt.read()
            elif backend == 'png':
                plot_div = self.plot_png_data(plot_path)

        return plot_div

    def rating_csv(self):
        'Returns a csv-like list of rating-values for this flow.'
        return CSVRow(self._filename, self.hash, self.ratings)

    def html_repr(self):
        'Returns a dict of "meta" data and "metrics".'
        from socket import inet_ntoa

        def create_metric_data(m):
            return [
              '{:.2f}, {:.2f}'.format(m['iat_avg'], m['iat_std']),
              '{:.2f}, {:.2f}'.format(m['traffic_avg'], m['traffic_std']),
              str(m['dscp_median']),
              str(m['bytes']),
              '{:.2f}, {:.2f}'.format(m['bytes_std'], m['bytes_avg']),
              str(m['packets'])]

        repr_data = [
          ('Source', '<a href="/#:src_ip={0}">{0}</a>:<a href="/#:sport={1}">{1}</a>'.format(inet_ntoa(self.srcip), self.srcport)),
          ('Destination', '<a href="/#:dst_ip={0}">{0}</a>:<a href="/#:dport={1}">{1}</a>'.format(inet_ntoa(self.dstip), self.dstport))]

        if hasattr(self, 'asn'):
            repr_data += [
              ('Autonomous system', '<a href="/#:asn={1}">{0} ({1})</a>'.format(self.as_name, self.asn)),
              ('BGP prefix', '<a href="/#:bgp={0}">{0}</a>'.format(self.bgp_prefix))]

        metric_name = [ 'Interarrival (avg, std)', 'Traffic (avg, std)',
          'DSCP (median)', 'Bytes', 'Bytes (std, avg)', 'Packets']
        metric_fwd = create_metric_data(self.fmetric)
        metric_bckwd = create_metric_data(self.bmetric)

        metric_data = zip(metric_name, metric_fwd, metric_bckwd)

        return { 'meta': repr_data, 'metric': metric_data }


class Flowfactory:
    'A class to store ratings and cached versions of flows and auto-load them.'

    plot_backends = ['png', 'plotly']

    def __init__(self, cache_path, store_filename):
        self.cache_path = cache_path
        self.store_filename = store_filename

    @staticmethod
    def pickle_name(filename, ext='.pickle'):
        'Returns a relative pickled filename from the given pcap.'
        from re import sub
        return sub('.pcap$', ext, path.basename(filename))

    def find_pickle(self, filename):
        'Tries to find a pickled filename (or None) for the given filename.'
        files = filter(
          lambda f: f == self.pickle_name(filename), listdir(self.cache_path))
        return files[0] if files else None

    def read_store(self):
        'Reads the store and returns a list of CSVRows.'
        if not path.isfile(self.store_filename):
            # create an empty store
            open(self.store_filename, 'a+').close()
            return []

        with open(self.store_filename, 'r') as in_store:
            reader = csv.reader(in_store)
            return map(lambda r: CSVRow(r[0], r[1], r[2:]), reader)

    def add_store(self, flow):
        'Adds a new or existing flow to the store.'
        current_store = [r for r in self.read_store()
          if r.filename != flow._filename and len(r.ratings) > 0]

        with open(self.store_filename, 'w+') as out_store:
            writer = csv.writer(out_store)
            for row in current_store + [flow.rating_csv()]:
                writer.writerow(csv_row_to_list(row))

    def save_flow(self, flow, save_store=True):
        'Saves or updates a flow and it\'s cached version.'
        pickle_file = self.cache_path + '/' + self.pickle_name(flow._filename)
        with open(pickle_file, 'w+') as out_file:
            pickle(flow, out_file)

        if save_store:
            self.add_store(flow)

    def get_flow(self, filename):
        '''Returns a flow for the given filename from the original file or the
           cached file and creates a cache file if it doesn't exists yet.'''
        has_pickle = self.find_pickle(filename)
        pickle_file = self.cache_path + '/' + self.pickle_name(filename)

        if not has_pickle:
            # Read file and save cached file
            ret_flow = flow(filename)
            # Don't save new flows in the store. On the one hand they don't
            # have any relevant ratings yet and on the other hand they
            # would override existing ratings which should be imported in
            # the following 'if' below.
            self.save_flow(ret_flow, save_store=False)
        else:
            # Restore file from cache
            with open(pickle_file, 'r') as in_file:
                ret_flow = unpickle(in_file)

            if ret_flow.hash != Flowfactory.head_hash(filename):
                # pcap-file was changed, remove it from cache and start clean
                remove(pickle_file)

                for plt_ext in self.plot_backends:
                    img_file = self.cache_path + '/' \
                      + self.pickle_name(filename, ext='.{}'.format(plt_ext))

                    if path.isfile(img_file):
                        remove(img_file)

                return self.get_flow(filename)

        # Check if there is a storage-entry for this flow and, if present
        # check both ratings and override the stored ones, if they differ.
        store_vals = [r for r in self.read_store() if r.filename == filename]
        if store_vals:
            store_val = store_vals[0]
            if ret_flow.ratings != store_val.ratings and ret_flow.hash == store_val.hash:
                ret_flow.ratings = store_val.ratings
            self.save_flow(ret_flow)

        return ret_flow

    @staticmethod
    def flow_list(input_dir):
        'Returns a sorted list of pcaps from input_dir.'
        flow_files = filter(lambda f: f.endswith('.pcap'), listdir(input_dir))
        return sorted(flow_files)

    def all_flows(self, input_dir):
        'Creates a list of pcaps in input_dir as a tuple with stored ratings.'
        flow_dicts = dict((path.basename(r[0]), r[2]) for r in self.read_store())
        return [(f, flow_dicts.get(f, [])) for f in Flowfactory.flow_list(input_dir)]

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
