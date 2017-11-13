#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SearchManager:
    def __init__(self, flow_factory, meta_manager, flow_store):
        self.flow_factory = flow_factory
        self.meta_manager = meta_manager
        self.flow_store = flow_store

    def _data_pair_dict(self):
        'Returns a dict of pcap_path -> (MetaFlow, Ratings)'
        mm_data = self.meta_manager.meta_store.copy()
        ff_data = map(lambda f: ('{}/{}'.format(self.flow_store, f[0]), f[1]),
          self.flow_factory.all_flows(self.flow_store))

        for ff in ff_data:
            if ff[0] not in mm_data:
                print('{} does not appear in the MetaManager!'.format(ff[0]))
                continue
            mm_data.update({ff[0]: (mm_data[ff[0]], ff[1])})

        for k, v in mm_data.items():
            if type(v) is not tuple:
                print('{} has no partner in the Flowfactory!'.format(k))
                del mm_data[k]

        return mm_data

    def data_pairs(self):
        'Returns a list of (MetaFlow, Ratings) for each (stored) pcap.'
        return self._data_pair_dict().values()

    @staticmethod
    def _filter_fun(data_pair, opts):
        for opt in opts:
            if opt[0] == 'as' and data_pair[0].as_name and opt[1] in data_pair[0].as_name:
                return True
            if opt[0] == 'asn' and data_pair[0].asn == opt[1]:
                return True
            if opt[0] == 'bgp' and opt[1] in data_pair[0].bgp_prefix:
                return True
            if opt[0] == 'source' and data_pair[0].src_ip == opt[1]:
                return True
            if opt[0] == 'destination' and data_pair[0].dst_ip == opt[1]:
                return True
            if opt[0] == 'port' and (str(data_pair[0].src_port) == opt[1] or str(data_pair[0].dst_port) == opt[1]):
                return True
            if opt[0] == 'rating' and opt[1] in data_pair[1]:
                return True
            if opt[0] == 'file' and opt[1] in data_pair[0].filename:
                return True
            return False

    def search(self, query):
        from parse import findall

        opts = [r.fixed for r in findall(':{:w}={:S}', query)]
        return filter(lambda dp: self._filter_fun(dp, opts), self.data_pairs())
