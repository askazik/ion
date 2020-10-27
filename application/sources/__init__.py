from application.sources.source import CausticsToZarr, CausticsFromZarr
from application.sources.graphics import draw_caustics

import pandas as pd

if __name__ == "__main__":
    # a = CausticsToZarr('~/!data/lab705/2016')
    # a.convert_to_zarr()

    # b = CausticsFromZarr('2013-10-01T04:10:30+0400_2013-10-01T06:21:48+0400.zarr')
    b = CausticsFromZarr('2016-01-19T13:26:42+0300_2016-01-19T15:17:00+0300.zarr')
    print([b.datetime_beg, b.datetime_end])

    i = 0
    for item in b.times:
        print(item)
        y = b.get_block_by_index(i)

        df = pd.DataFrame({'time': [x * b.DT for x in range(0, len(y))],
                           'amplitude': y})
        draw_caustics(df)
        i += 1


    # tree = b.make_tree()