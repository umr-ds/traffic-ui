#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import abort, redirect, request, route, run, static_file, template
from flowfactory import flow, Flowfactory
from os import listdir, makedirs, path

## Helper functions
def parse_config(filename):
    '''Reads the INI-config and returns a namedtuple called Config which
       contains the fields.'''
    from ConfigParser import ConfigParser
    from collections import namedtuple
    from json import loads as parse_list

    Config = namedtuple(
      'Config', ['host', 'port', 'input', 'cache', 'ratings', 'store'])

    config = ConfigParser()
    config.read(filename)

    return Config(
      config.get('httpd', 'host'),
      config.getint('httpd', 'port'),
      config.get('dirs', 'input').rstrip('/'),
      config.get('dirs', 'cache').rstrip('/'),
      parse_list(config.get('ratings', 'ratings')),
      config.get('ratings', 'store'))

def flow_from_filename(filename):
    '''Checks if a requested pcap-flow exists and returns the flow from the
       Flowfactory. The HTTP-connection will be aborted otherwise.'''
    fullpath = conf.input + '/' + filename

    if not path.isfile(fullpath):
        abort(404, 'No such file')
    if not fullpath.endswith('.pcap'):
        abort(403, 'Not allowed')
    if path.dirname(fullpath) != conf.input:
        abort(403, 'Not allowed')

    return flow_factory.get_flow(fullpath)

def rating_request(fun):
    '''The difference between adding and removing ratings is minimal. This
       helper-function will handle an add/del-request where all the logic,
       which is basically adding or removing an element, will be given as a
       lambda which receives the flow and the rating and should return a
       new list of ratings.'''
    filename  = request.forms.get('filename')
    rating = request.forms.get('rating')

    if filename  == None:
        return {'status': 'fail', 'msg': 'Parameter filename is missing'}
    if rating == None:
        return {'status': 'fail', 'msg': 'Parameter rating is missing'}

    req_flow = flow_from_filename(filename)
    req_flow.ratings = list(set(fun(req_flow, rating)))
    flow_factory.save_flow(req_flow)

    return {'status': 'ok', 'msg': 'noice :3'}

## List available pcaps (index)
@route('/')
def index():
    pcap_list = filter(lambda f: f.endswith('.pcap'), listdir(conf.input))
    return template('index', pcap_list=pcap_list)

## Flow details and plot
@route('/show/<filename>')
def show_pcap(filename):
    req_flow = flow_from_filename(filename)
    return template('flow_details', filename=filename, flow=req_flow, conf=conf)

@route('/plot/<filename>.png')
def plot_pcap(filename):
    req_flow = flow_from_filename(filename)
    filepath = req_flow.plot_path(flow_factory)
    return static_file(path.basename(filepath), root=path.dirname(filepath))

## Flow ratings
@route('/rating/list', method='POST')
def rating_list():
    filename  = request.forms.get('filename')
    if filename  == None:
        return {'status': 'fail', 'msg': 'Parameter filename is missing'}

    req_flow = flow_from_filename(filename)
    return {'status': 'ok', 'ratings': req_flow.ratings}
 
@route('/rating/add', method='POST')
def rating_add():
    return rating_request(lambda f, r: f.ratings + [r])

@route('/rating/del', method='POST')
def rating_del():
    return rating_request(lambda f, r: filter(lambda e: e != r, f.ratings))

## Static files (CSS, JS, …)
@route('/inc/<path:path>')
def static_route(path):
    return static_file(path, root='./inc')


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='path to config (default: ./config.ini)')
    args = parser.parse_args()

    if args.config == None and not path.isfile('./config.ini'):
        print('No config was found!\n' + \
          'Please place a config.ini in your current working directory or ' + \
          'supply a path by -c. If you\'re on a fresh instance, copy the ' + \
          'config-example.ini to config.ini and modify your copy.')
        exit(1)

    conf = parse_config(args.config if args.config != None else './config.ini')

    if not path.isdir(conf.cache):
        makedirs(conf.cache)

    import cymru
    cymru.DB_PATH = conf.cache + '/asn.db'

    flow_factory = Flowfactory(conf.cache, conf.store)
    run(host=conf.host, port=conf.port, debug=True, reloader=True)
