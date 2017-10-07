#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import abort, route, run, static_file
from flowfactory import flow, Flowfactory
from os import listdir, path

pcap_path = './input'
cache_path = './cache'

@route('/')
def index():
    pcap_list = filter(lambda f: f.endswith('.pcap'), listdir(pcap_path))
    list_body = map(lambda f: '<li><a href="/show/{0}">{0}</a></li>'.format(f), pcap_list)
    list_full = '<ul>{}</ul>'.format('\n'.join(list_body))
    return '<h1>Overview</h1>' + list_full

@route('/show/<filename>')
def show_pcap(filename):
    req_flow = flow_from_filename(filename)
    return '<img src="/plot/{0}.png" /><pre>{0}\n\n{1}</pre>'.format(filename, repr(req_flow))

@route('/plot/<filename>.png')
def plot_pcap(filename):
    req_flow = flow_from_filename(filename)
    flow_factory = Flowfactory(cache_path)

    filepath = req_flow.plot_path(flow_factory)
    return static_file(path.basename(filepath), root=path.dirname(filepath))

def flow_from_filename(filename):
    flow_factory = Flowfactory(cache_path)
    fullpath = pcap_path + '/' + filename

    if not path.isfile(fullpath):
        abort(404, 'No such file')
    if not fullpath.endswith('.pcap'):
        abort(403, 'Not allowed')
    if path.dirname(fullpath) != pcap_path:
        abort(403, 'Not allowed')

    return flow_factory.get_flow(fullpath)


if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True, reloader=True)
