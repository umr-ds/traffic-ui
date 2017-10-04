#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import abort, route, run, static_file
from flowinspector import flow
from io import BytesIO
from os import listdir, path

pcap_path = './input'
img_cache_path = './cache'

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
    img_name = req_flow.hash + '.png'
    plot_path = img_cache_path + '/' + img_name

    if not path.isfile(plot_path):
        import matplotlib
        matplotlib.use('Agg')

        import matplotlib.pyplot as plt
        plt.rcParams['figure.figsize'] = (9, 7)

        plot = req_flow.show(show=False)
        plot.savefig(plot_path, format='png')
        plot.close()

    return static_file(img_name, root=img_cache_path)

def flow_from_filename(filename):
    fullpath = pcap_path + '/' + filename

    if not path.isfile(fullpath):
        abort(404, 'No such file')
    if not fullpath.endswith('.pcap'):
        abort(403, 'Not allowed')
    if path.dirname(fullpath) != pcap_path:
        abort(403, 'Not allowed')

    req_flow = flow(fullpath)
    req_flow.lookupASN()
    return req_flow


if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True, reloader=True)
