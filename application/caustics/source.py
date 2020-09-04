import datetime
import os
import pytz
import glob
import zarr


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
    result = None

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
    TZ = pytz.timezone('Europe/Moscow')
    PREFIX = 'T'

    def __init__(self, path='.', datetime_beg=None, datetime_end=None):
        path = os.path.abspath(path)
        if os.path.isdir(path):
            self._path = path
        else:
            raise Exception("Validate given path for dataset: {}".format(path))

        self._datetime_beg = datetime_beg
        self._datetime_end = datetime_end

        self._sources = []
        self._init()

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
        file_list = glob.glob(os.path.join(self._path, '{0}???????.???'.format(CausticSource.PREFIX)))
        for item in file_list:
            try:
                data_datetime, data_length = is_valid_file(item)
            except Exception as ex:
                print("Filename {0} parsing error: {1}".format(item, ex))
                continue
            if data_datetime:
                source = {'filename': item, 'datetime': data_datetime, 'length': data_length}
                self._sources.append(source)
        print('Here are {0} data files.'.format(len(self._sources)))

    def _compose_out_filename(self, str_beg, str_end):
        """Compose filename for output data file"""
        if not str_beg:
            str_beg = self._datetime_beg.strftime('%Y-%m-%d')
        if not str_end:
            str_end = self._datetime_beg.strftime('%Y-%m-%d')
        return str_beg + '_' + str_end

    def convert_to_zarr(self, str_beg=None, str_end=None, out_filename=None):
        """Create zarr file for data between datetime_beg and datetime_end."""

        if not out_filename:
            out_filename = self._compose_out_filename(str_beg, str_end) + '.zarr'

        if not str_end:
            end = self._datetime_end
        else:
            end = datetime.datetime.strptime(str_end, '%Y-%m-%d')

        if not str_beg:
            beg = self._datetime_beg
        else:
            beg = datetime.datetime.strptime(str_beg, '%Y-%m-%d')


if __name__ == "__main__":
    a = CausticSource('./2016')
    print(a.sources)
