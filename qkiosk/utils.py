import pandas as pd
import numpy as np

def digits(n=2):
  pd.set_option('display.float_format', lambda x: '%.2f' % x)

def _full(full=False):
  pd.options.display.max_columns = None
  pd.options.display.max_rows = None

def is_documented_by(original):
  def wrapper(target):
    target.__doc__ = original.__doc__
    return target
  return wrapper

# run-length encoding
class _RLE:
    def __init__(self, lengths, values):
        self._lengths = lengths
        self._values = values

    def __repr__(self):
        return "values: "+str(self._values)+"\nlengths: "+str(self._lengths)

    @property
    def lengths(self):
       return self._length

    @lengths.setter
    def lengths(self,l):
        self._lengths = l

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self,v):
        self._values = v

    def inverse(self):
        x = []
        i = 0
        while i < len(self._values):
            x += [self._values[i]] *  self._lengths[i]
            i += 1
        return x

def rle(data):
    values = []
    lengths = []
    i = 0
    while i < len(data):
        count = 1
        while i + 1 < len(data) and data[i] == data[i + 1]:
            count += 1
            i += 1
        lengths.append(count)
        values.append(data[i])
        
        i += 1
    return _RLE(lengths,values)

def locf(data):
    rs = rle(data)
    v = rs.values
    S = np.nan
    for i in range(0, len(v)):
        if not np.isnan(v[i]):
            S = v[i]
        elif np.isnan(v[i]) and not np.isnan(S):
            v[i] = S

    rs.values = v
    x = rs.inverse()
    return x

def addTTM(data):
    for q in [1,2,3,4]:
        data.loc[data.fqtr == q,['fqpy']] = data.loc[data.fqtr == q,'fq'].shift(1)
        data.loc[data.fqtr == q,['fytdpy']] = data.loc[data.fqtr == q,'fytd'].shift(1)

    data.loc[data.fqtr == 4,['ann']] = data.loc[data.fqtr == 4,'fytd'].copy()
    data['lastann'] = locf(list(data['ann']))

    data['ttm'] = data['ann'].copy()
    data.loc[np.isnan(data.ann),['ttm']] = (data.loc[np.isnan(data.ann)].lastann + data.loc[np.isnan(data.ann)].fq - data.loc[np.isnan(data.ann)].fqpy)
    # FIXME: for BS this needs to be mean
    data = data.drop('lastann', axis=1)

    return data
