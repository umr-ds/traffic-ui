#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SearchManager:
    '''The SearchManager combines the data from the Flowfactory and the
       MetaManager to guarantee best search results based on queries.

       Queries will be logical AND-combined. The type of the query can
       be writen with a colon followed by the tag.

        :as=Foerder
        :asn=2323
        :bgp=123.123.123.123/24
        :source=10.0.0.1
        :dest=10.0.0.1
        :rating=upload
        :file=my-snip.pcap
       '''

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
    def _query_splitter(query):
        'Creates a list of tuples (key, query) for search keyboards.'
        import re

        pattern = re.compile(':([a-z]+)=(\S+)')
        for part in re.split('\s+', query):
            part_match = pattern.search(part)
            if part_match:
                yield part_match.group(1, 2)
            else:
                yield (None, part)

    @staticmethod
    def _filter_fun(data_pair, queries):
        'Checks if a data_pair matches a query from _query_splitter.'
        chks = {
            # str/None -> ((data_pair, query) -> bool)
            'as':     lambda dp, q: dp[0].as_name and q in dp[0].as_name,
            'asn':    lambda dp, q: str(dp[0].asn) == q,
            'bgp':    lambda dp, q: dp[0].bgp_prefix and q in dp[0].bgp_prefix,
            'source': lambda dp, q: dp[0].src_ip == q,
            'dest':   lambda dp, q: dp[0].dst_ip == q,
            'port':   lambda dp, q: str(dp[0].src_port) == q or str(dp[0].dst_port) == q,
            'rating': lambda dp, q: q in dp[1],
            'file':   lambda dp, q: q in dp[0].filename
        }

        for query in queries:
            if query[0] is not None:
                chk = chks[query[0]]
                if not chk(data_pair, query[1]):
                    return False
            else:
                flag = False
                for chk in chks.values():
                    if chk(data_pair, query[1]):
                        flag = True
                if not flag:
                    return False
        return True

    def search(self, query):
        'Returns a list of matching data_pairs for a query.'
        queries = list(self._query_splitter(query))
        return filter(lambda dp: self._filter_fun(dp, queries), self.data_pairs())
