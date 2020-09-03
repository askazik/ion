import datetime
import os
import sys
import pandas as pd
import pytz


def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")

    return dt


def parse_filename(filename):
    """Parse name of file for get datetime of samples begin"""
    result = None

    if len(filename) == 12 & filename[0] == 'T':  # new file format
        year = 2000 + int(filename[1:2])
        month = int(filename[3], 16)
        day = int(filename[4:5])
        hour = int(filename[6:7])
        minute = int(filename[9:10])
        sec = 10 * int(filename[11])
        result = datetime.datetime(year, month, day, hour, minute, sec)

    return result


def is_valid_file(filename):
    """Check current data file."""

    result = None
    try:
        if os.stat(filename).st_size >= 2:
            result = parse_filename(filename)
    except IOError as err:
        print("Error reading the file {0}: {1}".format(filename, err))

    return result


class CausticSource(object):
    DT = 0.0002505  # real data time step, s
    TZ = pytz.timezone('Europe/Moscow')

    def __init__(self, path=None, datetime_beg=None, datetime_end=None):
        self._path = path
        self._datetime_beg = datetime_beg
        self._datetime_end = datetime_end

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

    def _init(self):
        pass

    def get_paths(self, df):
        paths = {}
        self._names = []
        for phrase, name, filepath in zip(df.phrase, df.name, df.filepath):
            if phrase not in paths:
                paths[phrase] = {}
            paths[phrase][name] = filepath
            if name not in self._names:
                self._names.append(name)
        return paths

    @staticmethod
    def mkdir(*dirs):
        for directory in dirs:
            if not os.path.exists(directory):
                os.mkdir(directory)

    @staticmethod
    def read_csv(filepath, **kwargs):
        try:
            with open(filepath, "rb") as file:
                df = pd.read_csv(file, **kwargs)
                return df
        except Exception as error:
            sys.stderr.write(f"{error}\n")

    @staticmethod
    def write_csv(filepath, df, **kwargs):
        try:
            df.to_csv(filepath, **kwargs)
        except Exception as error:
            sys.stderr.write(f"{error}\n")


if __name__ == "__main__":
    a = is_valid_file('test.txt')
