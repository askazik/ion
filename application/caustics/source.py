import datetime
import os
import pytz
import glob
import zarr
import numpy as np
from multiprocessing import Pool
from numcodecs import Blosc


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
            data_datetime = parse_filename(filename)
        else:
            raise Exception("Empty file: {}".format(filename))
    except IOError as err:
        print("Error reading the file {0}: {1}".format(filename, err))

    return data_datetime, data_length


class CausticSource(object):
    DT = 0.0002505  # real data time step, s
    TZ = 'Europe/Moscow'
    PREFIX = 'T'

    def __init__(self, path='.', datetime_beg=None, datetime_end=None):
        path = os.path.abspath(path)
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
        file_list = glob.glob(os.path.join(self._path, '{0}???????.???'.format(self.PREFIX)))

        _datetimes = []
        _lengths = []
        for item in file_list:
            try:
                data_datetime, data_length = is_valid_file(item)
                _lengths.append(data_length)
            except Exception as ex:
                print("Filename {0} parsing error: {1}".format(item, ex))
                continue
            if data_datetime:
                _datetimes.append(data_datetime)
                source = {'filename': item, 'datetime': data_datetime, 'length': data_length}
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
            str_beg = self._datetime_beg.strftime('%Y-%m-%d %H:%M')
        if not str_end:
            str_end = self._datetime_end.strftime('%Y-%m-%d %H:%M')
        return str_beg + ' _ ' + str_end

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
        root.attrs['DT'] = self.DT
        root.attrs['TZ'] = self.TZ

        raw = root.create_group('raw')
        raw.attrs['DT'] = self.DT
        raw.attrs['TZ'] = self.TZ

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
        z_created = raw.zeros('created', shape=(len(self._sources), ), dtype='M8[D]')
        z_created[:] = axis_datetime

        print(root.tree())


if __name__ == "__main__":
    a = CausticSource('/media/askazik/Data/!data/kuleshov/2013')
    # a = CausticSource('./2013')
    a.convert_to_zarr()
