#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import abort, response, route, run
from flowinspector import flow
from io import BytesIO
from os import listdir, path

pcap_path = './input'

@route('/')
def index():
    pcap_list = filter(lambda f: f.endswith('.pcap'), listdir(pcap_path))
    list_body = map(lambda f: '<li><a href="/show/{0}">{0}</a></li>'.format(f), pcap_list)
    list_full = '<ul>{}</ul>'.format('\n'.join(list_body))
    return '<h1>Overview</h1>' + list_full

@route('/show/<filename>')
def show_pcap(filename):
    fullpath = check_fetch_fullpath(filename)
    req_flow = flow(fullpath)
    req_flow.lookupASN()
    return '<img src="/plot/{0}" /><pre>{0}\n\n{1}</pre>'.format(filename, repr(req_flow))

@route('/plot/<filename>')
def plot_pcap(filename):
    import matplotlib
    matplotlib.use('Agg')

    import matplotlib.pyplot as plt
    plt.rcParams['figure.figsize'] = (9, 7)

    fullpath = check_fetch_fullpath(filename)
    req_flow = flow(fullpath)
    req_flow.lookupASN()
    plt = req_flow.show(show=False)

    imgdata = BytesIO()
    plt.savefig(imgdata, format='png')
    imgdata.seek(0)

    plt.close()

    response.content_type = 'image/png'
    return imgdata

def check_fetch_fullpath(filename):
    fullpath = pcap_path + '/' + filename
    if not path.isfile(fullpath):
        abort(404, 'No such file')
    if not fullpath.endswith('.pcap'):
        abort(403, 'Not allowed')
    if path.dirname(fullpath) != pcap_path:
        abort(403, 'Not allowed')
    return fullpath


if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True, reloader=True)
