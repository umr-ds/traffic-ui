#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import abort, redirect, request, route, run, static_file, template
from flowfactory import flow, Flowfactory
from os import makedirs, path


# Helper functions
def parse_config(filename):
    '''Reads the INI-config and returns a namedtuple called Config which
       contains the fields.'''
    from ConfigParser import ConfigParser
    from collections import namedtuple
    from json import loads as parse_list

    Config = namedtuple(
      'Config',
      ['host', 'port', 'input', 'cache', 'ratings', 'enforce', 'store'])

    config = ConfigParser()
    config.read(filename)

    return Config(
      config.get('httpd', 'host'),
      config.getint('httpd', 'port'),
      config.get('dirs', 'input').rstrip('/'),
      config.get('dirs', 'cache').rstrip('/'),
      parse_list(config.get('ratings', 'ratings')),
      config.getboolean('ratings', 'enforce'),
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
    filename = request.forms.get('filename')
    rating = request.forms.get('rating')

    if filename is None:
        return {'status': 'fail', 'msg': 'Parameter filename is missing'}
    if rating is None:
        return {'status': 'fail', 'msg': 'Parameter rating is missing'}

    req_flow = flow_from_filename(filename)
    req_flow.ratings = list(set(fun(req_flow, rating)))
    flow_factory.save_flow(req_flow)

    return {'status': 'ok', 'msg': 'Rating changed'}


# List available pcaps (index)
@route('/')
def index():
    return template('index', flows=flow_factory.all_flows(conf.input))


# Flow details and plot
@route('/show-random')
def show_random():
    from random import choice
    pcaps = [f[0] for f in flow_factory.all_flows(conf.input) if f[1] == []]
    if not pcaps:
        return template('base', title='Random plot',
          base='<p>Sorry, but there are no unrated plots to show left.</p>')
    else:
        redirect('/show/{}'.format(choice(pcaps)))


@route('/show/<filename>')
def show_pcap(filename):
    req_flow = flow_from_filename(filename)

    flow_files = Flowfactory.flow_list(conf.input)
    index = flow_files.index(filename)
    succ_id = index+1 if index < len(flow_files)-1 else 0

    return template('flow_details',
      filename=filename, flow=req_flow, conf=conf,
      prec=flow_files[index-1], succ=flow_files[succ_id])


@route('/plot/<filename>.png')
def plot_pcap(filename):
    req_flow = flow_from_filename(filename)
    filepath = req_flow.plot_path(flow_factory)
    return static_file(path.basename(filepath), root=path.dirname(filepath))


# Flow ratings
@route('/rating/list', method='POST')
def rating_list():
    filename = request.forms.get('filename')
    if filename is None:
        return {'status': 'fail', 'msg': 'Parameter filename is missing'}

    req_flow = flow_from_filename(filename)
    return {'status': 'ok', 'ratings': req_flow.ratings}


@route('/rating/add', method='POST')
def rating_add():
    rating = request.forms.get('rating')
    if conf.enforce and rating not in conf.ratings:
        return {'status': 'fail', 'msg': 'Rating is not allowed.'}

    return rating_request(lambda f, r: f.ratings + [r])


@route('/rating/del', method='POST')
def rating_del():
    return rating_request(lambda f, r: filter(lambda e: e != r, f.ratings))


# Static files (CSS, JS, …)
@route('/inc/<path:path>')
def static_route(path):
    return static_file(
      path, root=path.dirname(path.realpath(__file__)) + '/inc')


if __name__ == "__main__":
    import argparse
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
    run(host=conf.host, port=conf.port, debug=True, reloader=True)
