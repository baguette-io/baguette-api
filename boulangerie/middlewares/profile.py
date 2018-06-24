#-*- coding:utf-8 -*-
"""
cProfile middleware for Django.
 | When adding *debug* as parameter in the GET request
 | There is also the *sort* parameter, default to 'time',
 see https://docs.python.org/2/library/profile.html#pstats.Stats.sort_stats.
the query will be profiled using cProfile.
"""
import cProfile
import pstats
import StringIO

class Profile(object):

    def __init__(self):
        self.profiler = None


    def process_view(self, request, callback, callback_args, callback_kwargs):
        if '__debug__' in request.GET:
            self.profiler = cProfile.Profile()
            args = (request,) + callback_args
            return self.profiler.runcall(callback, *args, **callback_kwargs)


    def process_response(self, request, response):
        if '__debug__' in request.GET:
            result = StringIO.StringIO()
            self.profiler.create_stats()
            stats = pstats.Stats(self.profiler, stream=result)
            stats.strip_dirs().sort_stats(request.GET.get('sort', 'time')).print_stats()
            response.content = result.getvalue()
            response['Content-type'] = 'text/plain'
        return response
