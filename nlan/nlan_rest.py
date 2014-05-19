# 2014/5/19

import os, sys, urlparse
from wsgiref import util, simple_server
from cStringIO import StringIO

class RestApi(object):
    
    def __init__(self):
        pass 
        
    def __call__(self, environ, start_response):

        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO'].split('/')
        router = None
        module = None
        _index = None
        if len(path) > 1:
            router = path[1]
        if len(path) > 2:
            module = path[2]
        if len(path) > 3:
            _index = path[3]
        
        query = self.query_string(environ)
        out = StringIO()

        if method == 'GET':
            start_response('200 OK', [('Content-type', 'text/plain')])
            print >>out, router
            print >>out, module
            print >>out, _index
            print >>out, str(query)
            out.seek(0)
            return out 
        elif method == 'POST':
            return  
        elif method == 'DELETE':
            return  
        else:
            start_response('501 Not Implemented', [('Content-type', 'text/plain')])
            return 'Not Implemented'

    def query_string(self, environ):
        return dict(urlparse.parse_qsl(environ['QUERY_STRING']))
        
if __name__ == '__main__':

    host_ip = '0.0.0.0'
    port = 8888
    appl = RestApi()
        
    srv = simple_server.make_server(host_ip, port, appl)
    srv.serve_forever()
    
