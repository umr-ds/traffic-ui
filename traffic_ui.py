#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import abort, redirect, request, route, run, static_file
from flowfactory import flow, Flowfactory
from os import listdir, makedirs, path

## Config
pcap_path = './input'
cache_path = './cache'

## Helper functions
def flow_from_filename(filename):
    '''Checks if a requested pcap-flow exists and returns the flow from the
       Flowfactory. The HTTP-connection will be aborted otherwise.'''
    fullpath = pcap_path + '/' + filename

    if not path.isfile(fullpath):
        abort(404, 'No such file')
    if not fullpath.endswith('.pcap'):
        abort(403, 'Not allowed')
    if path.dirname(fullpath) != pcap_path:
        abort(403, 'Not allowed')

    return flow_factory.get_flow(fullpath)

def rating_request(filename, fun):
    '''The difference between adding and removing ratings is minimal. This
       helper-function will handle an add/del-request where all the logic,
       which is basically adding or removing an element, will be given as a
       lambda which receives the flow and the rating and should return a
       new list of ratings.'''
    rating = request.forms.get('rating')
    if rating == None:
        abort(500, 'parameter is missing')

    req_flow = flow_from_filename(filename)
    req_flow.ratings = list(set(fun(req_flow, rating)))

    flow_factory.save_flow(req_flow)
    redirect('/show/{}'.format(filename))

## List available pcaps (index)
@route('/')
def index():
    pcap_list = filter(lambda f: f.endswith('.pcap'), listdir(pcap_path))
    list_body = map(lambda f: '<li><a href="/show/{0}">{0}</a></li>'.format(f), pcap_list)
    list_full = '<ul>{}</ul>'.format('\n'.join(list_body))
    return '<h1>Overview</h1>' + list_full

## Flow details and plot
@route('/show/<filename>')
def show_pcap(filename):
    req_flow = flow_from_filename(filename)
    return '<img src="/plot/{0}.png" /><pre>{0}\n{1}\n\n{2}</pre>'.format(
      filename, ' '.join(req_flow.ratings), repr(req_flow))

@route('/plot/<filename>.png')
def plot_pcap(filename):
    req_flow = flow_from_filename(filename)
    filepath = req_flow.plot_path(flow_factory)
    return static_file(path.basename(filepath), root=path.dirname(filepath))

## Flow ratings
@route('/rating/add/<filename>', method='POST')
def rating_add(filename):
    rating_request(filename, lambda f, r: f.ratings + [r])

@route('/rating/del/<filename>', method='POST')
def rating_del(filename):
    rating_request(filename, lambda f, r: filter(lambda e: e != r, f.ratings))

if __name__ == "__main__":
    if not path.isdir(cache_path):
        makedirs(cache_path)

    flow_factory = Flowfactory(cache_path)
    run(host='localhost', port=8080, debug=True, reloader=True)
