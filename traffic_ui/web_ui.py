#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import abort, redirect, request, route, run, static_file, template, TEMPLATE_PATH
from collections import namedtuple
from operator import itemgetter
from os import makedirs, path
from struct import unpack
from flowfactory import flow, Flowfactory
from metamanager import MetaManager
from searchmanager import SearchManager


# Config-object which will contain the configuration
Config = namedtuple('Config',
  ['host',          # httpd.host (localhost)
   'port',          # httpd.port (8080)
   'plot_backend',  # httpd.plotting (png)
   'upload_pass',   # httpd.upload_password (NONE)
   'input',         # dirs.input (NONE)
   'cache',         # dirs.cache (NONE)
   'store',         # ratings.store (NONE)
   'ratings',       # ratings.ratings (upload,download,interactive)
   'enforce'        # ratings.enforce (true)
])


# Helper functions
def parse_config(filename):
    '''Reads the INI-config and returns a namedtuple called Config which
       contains the fields.'''
    from ConfigParser import SafeConfigParser

    conf_parser = SafeConfigParser(defaults={
      # httpd
      'host': 'localhost',
      'port': 8080,
      'plotting': 'png',
      'upload_password': None,
      # dirs
      'input': '',
      'cache': '',
      # ratings
      'store': None,
      'ratings': 'upload,download,interactive',
      'enforce': True
    })
    conf_parser.read(filename)

    cfg = Config(
      conf_parser.get('httpd', 'host'),
      conf_parser.getint('httpd', 'port'),
      conf_parser.get('httpd', 'plotting'),
      conf_parser.get('httpd', 'upload_password'),

      conf_parser.get('dirs', 'input').rstrip('/'),
      conf_parser.get('dirs', 'cache').rstrip('/'),

      conf_parser.get('ratings', 'store'),
      conf_parser.get('ratings', 'ratings').split(','),
      conf_parser.getboolean('ratings', 'enforce'))

    if cfg.plot_backend not in Flowfactory.plot_backends:
        print('Unsupported httpd.plotting-backend.')
        exit(1)
    if cfg.upload_pass is None:
        print('No valid httpd.upload_password was specified.')
        exit(1)
    if cfg.input == '' or not path.isdir(cfg.input):
        print('No valid dirs.input was specified.')
        exit(1)
    if cfg.cache == '':
        print('No valid dirs.cache was specified.')
        exit(1)
    if cfg.store is None:
        print('No valid ratings.store was specified.')
        exit(1)

    return cfg


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
    return template('index', ratings=conf.ratings)


# Flow details and plot
@route('/show-random')
def show_random():
    from random import choice
    pcaps = [f[0] for f in flow_factory.all_flows(conf.input) if f[1] == []]
    if not pcaps:
        return template('base', title='Random plot',
          base='<p>Sorry, but there are no unrated plots to show left.</p>',
          ratings=conf.ratings)
    else:
        redirect('/show/{}'.format(choice(pcaps)))


@route('/show/<filename>')
def show_pcap(filename):
    req_flow = flow_from_filename(filename)

    flow_files = Flowfactory.flow_list(conf.input)
    index = flow_files.index(filename)
    succ_id = index+1 if index < len(flow_files)-1 else 0

    return template('flow_details',
      filename=filename, flow=req_flow,
      plot=req_flow.plot_data(flow_factory, conf.plot_backend),
      conf=conf, prec=flow_files[index-1], succ=flow_files[succ_id],
      ratings=conf.ratings)


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


@route('/search', method='POST')
def search():
    query = request.forms.get('q')
    if query is None:
        return {'status': 'fail', 'msg': 'No given query \'q\'.'}
    result = [{'file': path.basename(r[0].filename), 'ratings': r[1]} 
              for r in search_manager.search(query)]
    return {'status': 'ok', 'result': sorted(result, key=itemgetter('file'))}


@route('/search/hist')
def search_hist():
    return {'history': search_manager.history()}


@route('/upload', method='GET')
def upload_get():
    return template('upload', ratings=conf.ratings)


@route('/upload', method='POST')
def upload_post():
    upload = request.files.get('upload')
    password = request.forms.get('password')

    if password != conf.upload_pass:
        print('Upload failed due to a wrong password!')
        return template('base', title='Upload',
          base='<p>Password is wrong. This incident will be reported.</p>',
          ratings=conf.ratings)

    upload_data = upload.file.read()
    upload.file.close()

    magic_numb = unpack('>I', upload_data[:4])[0]
    _, ext = path.splitext(upload.filename)
    output_name = '{}/{}'.format(conf.input, upload.filename)

    if magic_numb != 0xd4c3b2a1 or ext != '.pcap':
        return template('base', title='Upload',
          base='<p>Sorry, but your file doesn\'t seems to be a pcap-file.</p>',
          ratings=conf.ratings)

    if path.isfile(output_name):
        return template('base', title='Upload',
          base='<p>Sorry, but a flow for this name does already exists.</p>',
          ratings=conf.ratings)

    with open(output_name, 'wb') as f:
        f.write(upload_data)

    redirect('/show/{}'.format(upload.filename))


# Static files (CSS, JS, …)
@route('/inc/<static_path:path>')
def static_route(static_path):
    return static_file(
      static_path, root=path.dirname(path.realpath(__file__)) + '/../inc')


def main():
    global conf, flow_factory, meta_manager, search_manager

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
    meta_manager = MetaManager(flow_factory, conf.input, background=True)
    search_manager = SearchManager(flow_factory, meta_manager, conf.input)

    TEMPLATE_PATH.insert(
      0, path.realpath(path.dirname(path.realpath(__file__)) + '/../views/'))
    run(host=conf.host, port=conf.port, debug=True)


if __name__ == '__main__':
    main()
