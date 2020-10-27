import datetime
import os
import re
import pytz
import zarr
import numpy as np
import pandas as pd
from multiprocessing import Pool
from numcodecs import Blosc

import decorators


def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")

    return dt


def parse_filename(filepath):
    """Parse name of file for get datetime of samples begin"""

    filename = os.path.split(filepath)[1]
    if len(filename) == 12:  # new file format
        year = 2000 + int(filename[1:3])
        month = int(filename[3], 16)
        day = int(filename[4:6])
        hour = int(filename[6:8])
        minute = int(filename[9:11])
        sec = 6 * int(filename[11])
        result = datetime.datetime(year, month, day, hour, minute, sec)
    else:
        raise Exception("Filename length <> 12: {}".format(len(filename)))

    return result


def is_valid_file(filename):
    """Check current data file."""

    data_datetime = None
    data_length = 0
    try:
        data_length = int(os.stat(filename).st_size / 2)
        if data_length >= 1:
            data_datetime = np.datetime64(parse_filename(filename))
        else:
            raise Exception("Empty file: {}".format(filename))
    except IOError as err:
        print("Error reading the file {0}: {1}".format(filename, err))

    return data_datetime, data_length


def is_valid_filename(prefix, filename):
    """Check filename."""

    is_valid = False
    pattern_string = '^' + prefix + r'\d{2}[0-9a-f]\d{4}.\d{3}$'
    pattern = re.compile(pattern_string.lower())
    if pattern.match(filename.lower()).group():
        is_valid = True

    return is_valid


# Генератор для имён файлов с каустиками
def files(prefix, path):
    for file in os.listdir(path):
        filepath = os.path.join(path, file)
        if os.path.isfile(filepath):
            # Нужно проверить на соответствие шаблону!!!
            if is_valid_filename(prefix, file):
                yield filepath
            else:
                print('<{0}> - has not valid caustic filename!'.format(filepath))

    # for file in files("."):
    #     print(file)


class CausticsToZarr(object):
    DT = 0.0002505  # real data time step, s
    TZ = 'Europe/Moscow'
    PREFIX = 'T'

    def __init__(self, path='.', datetime_beg=None, datetime_end=None):
        path = os.path.abspath(os.path.expanduser(path))
        if os.path.isdir(path):
            self._path = path
        else:
            raise Exception("Validate given path for dataset: {}".format(path))

        self.tz = pytz.timezone(self.TZ)
        self._datetime_beg = datetime_beg
        self._datetime_end = datetime_end

        self._sources = []
        self._length_min = 0
        self._length_max = 0
        self.result_list = []
        self.z_raw = None

        self._init()

    def reader(self, i, filename):
        data = np.fromfile(filename, dtype='int16')
        self.z_raw[i, 0:len(data)] = data
        # return data

    def log_result(self, result):
        # This is called whenever foo_pool(i) returns a result.
        # result_list is modified only by the main process, not the pool workers.
        self.result_list.append(result)

    @property
    def path(self):
        return self._path

    @property
    def datetime_beg(self):
        return self._datetime_beg

    @property
    def datetime_end(self):
        return self._datetime_end

    @property
    def sources(self):
        return self._sources

    def _init(self):
        print('Scan {0} for data files...'.format(self._path))

        _datetimes = []
        _lengths = []
        for file in files(self.PREFIX, self._path):
            try:
                data_datetime, data_length = is_valid_file(file)
                _lengths.append(data_length)
            except Exception as ex:
                print("Filename {0} parsing error: {1}".format(file, ex))
                continue
            if data_datetime:
                _datetimes.append(data_datetime)
                source = {'filename': file, 'datetime': data_datetime, 'length': data_length}
                self._sources.append(source)
        print('Here are {0} data files.'.format(len(self._sources)))
        self._sources = sorted(self._sources, key=lambda i: i['datetime'])

        _datetimes.sort()
        self._datetime_beg = _datetimes[0]
        self._datetime_end = _datetimes[-1]
        print('Begin: {0}, End {1}'.format(self._datetime_beg, self._datetime_end))

        _lengths.sort()
        self._length_min = _lengths[0]
        self._length_max = _lengths[-1]

    def _compose_out_filename(self, str_beg, str_end):
        """Compose filename for output data file"""
        if not str_beg:
            # str_beg = self._datetime_beg.strftime('%Y-%m-%d_%H:%M')
            str_beg = np.datetime_as_string(self._datetime_beg, unit = 's',timezone=pytz.timezone(self.TZ))
        if not str_end:
            # str_end = self._datetime_end.strftime('%Y-%m-%d_%H:%M')
            str_end = np.datetime_as_string(self._datetime_end, unit='s', timezone=pytz.timezone(self.TZ))
        return str_beg + '_' + str_end

    def convert_to_zarr(self, str_beg=None, str_end=None, out_filename=None, out_path=None):
        """Create zarr file for data between datetime_beg and datetime_end."""

        if not str_end:
            end = self._datetime_end
        else:
            end = datetime.datetime.strptime(str_end, '%Y-%m-%d')

        if not str_beg:
            beg = self._datetime_beg
        else:
            beg = datetime.datetime.strptime(str_beg, '%Y-%m-%d')

        if not out_filename:
            store = self._compose_out_filename(str_beg, str_end) + '.zarr'
        else:
            store = out_filename

        if out_path:
            store = os.path.join(out_path, store)

        # create hierarchy
        root = zarr.open(store, mode='w')  # means create (fail if exists)
        # FIXME: Remove these root attributes
        root.attrs['DT'] = self.DT
        root.attrs['TZ'] = self.TZ
        raw = root.create_group('raw')

        # Zarr provides support for chunk-level synchronization.
        # This array is safe to read or write within a multi-threaded program.
        compressor = Blosc(cname='zstd', clevel=3, shuffle=Blosc.BITSHUFFLE)
        self.z_raw = raw.zeros('source',
                               shape=(len(self._sources), self._length_max),
                               chunks=(1, self._length_max),
                               dtype='i2',
                               compressor=compressor,
                               synchronizer=zarr.ThreadSynchronizer())
        self.z_raw[:] = np.nan

        i = 0
        axis_datetime = []
        pool = Pool(processes=6)
        for item in self._sources:
            if beg <= item['datetime'] <= end:
                axis_datetime.append(item['datetime'])
                cur_filename = item['filename']
                pool.apply_async(self.reader, args=(i, cur_filename, ), callback=self.log_result)
                i += 1
        pool.close()
        pool.join()
        # print(self.result_list)

        # append created axis
        # FIXME: set an datetime axis (for given TZ!!!)
        # s -> seconds precision!!!
        z_created = raw.zeros('created', shape=(len(self._sources), ), dtype='M8[s]')
        z_created[:] = axis_datetime

        print(root.tree())


class CausticsFromZarr(object):

    def __init__(self, path):

        path = os.path.abspath(os.path.expanduser(path))
        try:
            self._zarr = zarr.open(path, mode='r')
            self._path = path
        except Exception as e:
            raise Exception("Validate given path for dataset: {0}. Exception: {1}".format(path, str(e)))

        if 'DT' in self._zarr.attrs:
            self._DT = self._zarr.attrs['DT']

        if 'TZ' in self._zarr.attrs:
            self._TZ = self._zarr.attrs['TZ']

        self._source = self._zarr['raw']['source']
        self._created = self._zarr['raw']['created']
        self._datetime_beg = self._created[0]
        self._datetime_end = self._created[-1]

    @property
    def path(self):
        return self._path

    @property
    def datetime_beg(self):
        return self._datetime_beg

    @property
    def datetime_end(self):
        return self._datetime_end

    @property
    def DT(self):
        return self._DT

    @property
    def TZ(self):
        return self._TZ

    @property
    def times(self):
        for _item in self._created:
            yield _item

    @property
    def tree(self):
        return self.make_tree()

    @staticmethod
    def make_node(title, key, children):
        out = {
            'title': title,
            'key': key}
        if children:
            out['children'] = children
        return out

    def get_block_by_index(self, idx):
        """Извлечение блока по индексу (порядковому номеру) в открытом файле.
        Вопрос: А если открыть в объекте много файлов?"""
        return self._source[idx]

    def get_block_by_name(self, idx):
        """Извлечение блока по имени в открытом файле.
        Вопрос: А если открыть в объекте много файлов?"""
        pass

    def get_blocks_interval_by_index(self, indexes):
        # for index in indexes:
        #     yield index
        pass

    def get_blocks_interval_by_date(self, date1, date2):
        pass

    def make_tree(self):
        """Сборка текущего временного дерева из списка имен извлечённых блоков (файлов каустик)"""
        _tree = {
            'title': 'Caustics',
            'key': '0',
            'children': []}

        year = None
        month = None
        day = None
        dates = pd.DatetimeIndex(self.times)
        for date in dates:
            cur_year = date.year
            cur_month = date.month
            cur_day = date.day

        return _tree
