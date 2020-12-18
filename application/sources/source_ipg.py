# http://ipg.geospace.ru/graph/ion/ionogram2_cd.php?st=37701&dtime=2020-11-18T10:45:00&show_o=0&show_x=1&contrast=1&profile=0
from datetime import datetime, timedelta

import pytz
from tzlocal import get_localzone
from string import Template
from abstract import AbstractSource
import shadow_useragent

from proxy_requests import ProxyRequests

STATIONS_LIST = {
    32508: {'begin': '2014-12-12T17:59:57'},
    34502: {'begin': '2011-02-21T15:00:00'},
    34504: {'begin': '2013-12-27T07:15:00'},
    34506: {},
    37701: {},
    38501: {},
    39601: {},
    43501: {},
    45602: {},
    46501: {}
}
TASKS_ON_PAGE = 100
IONOGRAM_DELTA = 15


# headers = {
#     'User-Agent': 'Some custom user agent',
# }
#
# r = ProxyRequests("url here")
# r.set_headers(headers)
# r.post_with_headers({"key1": "value1", "key2": "value2"})


# url = 'https://www.restwords.com/static/ICON.png'
# r = ProxyRequests(url)
# r.get()
# with open('out.png', 'wb') as f:
#     f.write(r.get_raw())


# Available data sources
class SourceClasses:
    class IPG(AbstractSource):
        base = 'http://ipg.geospace.ru/graph/ion/ionogram2_cd.php'
        template = Template('$base?st=$st&dtime=$dtime&show_o=$show_o&show_x=$show_x&contrast=1&profile=0')
        table = 'ipg'

        def __init__(self, st=None, dtime=None, tz=None):
            # Default (test) initialization
            if st is None:
                st = 37701
            if dtime is None:
                dtime = '2020-11-18T10:45:00'
            if tz is None:
                self.TZ = get_localzone()
            else:
                self.TZ = tz

            if not type(dtime) is str:
                raise TypeError('<dtime> must be string!')
            if not type(st) is str and not type(st) is int:
                raise TypeError('<st> must be string or int!')

            self._source = {
                'table': self.table,
                'TZ': self.TZ,
                'fields': {
                    'o': self.template.substitute(base=self.base, st=st, dtime=dtime, show_o=1, show_x=0),
                    'x': self.template.substitute(base=self.base, st=st, dtime=dtime, show_o=0, show_x=1),
                    'station': st,
                    'dtime': dtime
                }
            }

        @property
        def source(self):
            return self._source

    class RWM(AbstractSource):
        def __init__(self):
            self._source = {
            }

        @property
        def source(self):
            return self._source


class TasksDirector:

    def __init__(self):
        # Get available useragents
        self.ua = shadow_useragent.ShadowUserAgent()

    def perdelta(self, start, end, delta, source_name, **kwargs):
        curr = start
        D = delta * TASKS_ON_PAGE

        end_page = curr + D
        while curr <= end:
            datetimes = []

            while curr < end_page:
                datetimes.append(curr)
                curr += delta

            end_page = curr
            # outs = self.from_list(source_name, datetimes=datetimes, **kwargs)
            yield datetimes


        # return datetimes

    def from_interval(self, source_name, **kwargs):

        # Define an datetime interval
        tz_local = get_localzone()
        if 'tz' in kwargs:
            tz_source = pytz.timezone(kwargs['tz'])
        else:
            tz_source = tz_local

        if 'station' in kwargs:
            # Define datetimes list by interval with paging
            if 'datetime_begin' not in kwargs or not kwargs['datetime_begin']:
                datetime_begin = STATIONS_LIST[kwargs['station']]['begin']
            else:
                datetime_begin = kwargs['datetime_begin']
            # source tz
            _begin = datetime.strptime(datetime_begin, '%Y-%m-%dT%H:%M:%S')
            _begin = tz_source.localize(_begin)

            if 'datetime_end' not in kwargs or not kwargs['datetime_end']:
                # convert to source tz
                _end = datetime.now()
                _end = tz_local.localize(_end)
                if tz_local != tz_source:
                    _end = _end.astimezone(tz_source)
            else:
                datetime_end = kwargs['datetime_end']
                # source tz
                _end = datetime.strptime(datetime_end, '%Y-%m-%dT%H:%M:%S')
                _end = tz_source.localize(_end)

            # _begin and _end now in tz_source!!! not in UTC!!!
            sources = self.perdelta(_begin, _end, timedelta(minutes=IONOGRAM_DELTA), source_name, **kwargs)

        else:
            sources = None

        yield sources

    def from_list(self, source_name, **kwargs):
        sources = []
        targetClass = getattr(SourceClasses, source_name)
        if 'datetimes' in kwargs:
            for dt in kwargs['datetimes']:
                st = None
                if 'station' in kwargs:
                    st = kwargs['station']
                source = targetClass(st, dt).source

                # Pick a random user agent for the headers
                source['headers'] = {'User-Agent': self.ua.random}

                sources.append(source)

        return sources


# Only for test purposes!!!
if __name__ == "__main__":
    director = TasksDirector()
    # tasks = director.from_list('IPG', station=32508, datetimes=['2014-12-12T17:59:57'])
    tasks = director.from_interval('IPG', station=32508, tz='Europe/Moscow')
    while True:
        for item in tasks:
            print(item)

