import io, re, time
import requests
import copy
import numpy as np
import pandas as pd

import concurrent.futures

from .yyyymmdd import yyyymmdd, today
from .account import get_apikey

from .qkid import __reqQKID
_FNCODES = {}
def fncodes():
    if "codes" in _FNCODES:
        return _FNCODES["codes"]

    fncodes = __reqQKID("itemcodes/fn/codes")

    _FNCODES["codes"] = fncodes

    return fncodes

## this is insane that pandas requires global setting
pd.set_option('display.float_format', str)

class _Fn:
  def __init__(self, data, elapsed, view = 'asof', asof = today(), start = 20000101, end = 20991231, ticker=True, resps=[], qkid_items=None, full=False):
    self._data = data
    self._elapsed = elapsed
    self._view = view
    self._asof = asof
    self._ticker = ticker
    self._start = yyyymmdd(start)
    self._end = yyyymmdd(end)
    self._resps = resps
    self._qkid_items = qkid_items
    self._full = full
    self._selected = [i for i in range(0,len(qkid_items["id"]))]
    self._default_cols = ['cik','acceptance_time','stmt','item','filed','fpb','fpe','fqd','fp','fqtr','cyqtr','fq','fytd','ttm','ann','rstmt']

  def __repr__(self):
    nqkids = str(len(self._data))
    nitems = str(len(self._data[tuple(self._data.keys())[0]]))
    return "Fn: "+nitems+" items on "+nqkids+" companies"

  def select(self, items):
    from .qkid import cik
    
    if type(items) is not list: items = [items]

    selected = []
    for item in items:
      i = [i for i,ticker_item in enumerate([cik(int(id[:10])).to_ticker()[0]+"."+id[11:] for id in self._qkid_items['id']]) if ticker_item == item][0]
      selected.append(i)

    new = copy.copy(self)
    new._selected = selected
    return new

  def __getitem__(self,item):
    return self.select(item)

  @property
  def default_cols(self):
    return self._default_cols

  @default_cols.setter
  def default_cols(self, cols):
    self._default_cols = cols

  @property
  def qkid_items(self):
    return self._qkid_items

  @property
  def full(self):
    return self._full

  @property
  def data(self):
    return self._data

  @property
  def elapsed(self):
    return self._elapsed

  def start(self, start=20000101, inplace=False):
    if inplace is False:
        new = copy.copy(self)
        new._start = start
        return new

    self._start = yyyymmdd(start)
    return self

  def full(self, show=True, inplace=False):
    if inplace is False:
        new = copy.copy(self)
        new._full = show
        return new

    self._full = show
    return self

  def end(self, end=20991231, inplace=False):
    if inplace is False:
        new = copy.copy(self)
        new._end = end
        return new

    self._end = yyyymmdd(end)
    return self

  def asof(self, as_of=today(), inplace=False):
    if inplace is False:
        new = copy.copy(self)
        new._view = 'asof'
        return new

    self._view = 'asof' 
    return self

  def asfiled(self, inplace=False):
    if inplace is False:
        new = copy.copy(self)
        new._view = 'asfiled'
        return new

    self._view = 'asfiled' 
    return self

  def to_list(self):
    from .utils import addTTM
    x = []
    keep = None
    if self._view == "asof" :
      keep = 'last'

    if self._view == "asfiled":
      keep = 'first'

    for i in self._selected:
      qkid_item = self._qkid_items['id'][i]

      d = self._data["CIK"+qkid_item[0:10]][qkid_item[11:]]

      if keep is not None:
        d = d.drop_duplicates(subset="fpe",keep=keep)
        d = addTTM(d)


      x.append(d)

    return x

  def to_df(self):
    x = self.to_list()

    if len(x) == 0:
       return pd.DataFrame()

    df = pd.concat(x, axis=0, ignore_index=True)


    if self._full is not True:
      df = df.loc[:, self._default_cols]

    return df
    

  def to_ts(self, freq=None, ticker=None):
    from .qkid import cik

    keep = None
    if self._view == "asof":
      keep = 'last'
        
    if self._view == "asfiled":
      keep = 'first'

    if freq == None:
      freq = self._freq
    else:
      if type(freq) is not list: freq = [freq]

    if ticker == None:
      ticker = self._ticker

    all_column_names = []
    missing_column_names = []

    fdata = pd.DataFrame()
    data = self._data
    for qkid in data:
      for item in data[qkid]:
        
        d = data[qkid][item]
        if keep is not None:
          d = d.drop_duplicates(subset="fpe",keep=keep)
  
        column_names = ["{}.{}.{}".format(qkid,item,freq[0])]
        if ticker is True:
          column_names = ["{}.{}.{}".format(cik(int(qkid.lstrip("CIK"))).to_ticker()[0],item,freq[0])]
        all_column_names.append(column_names[0])
  
        if len(d) == 0:
          missing_column_names.append(column_names[0])
          continue
        else:
          df = pd.DataFrame(d[freq[0]].values, index=pd.to_datetime(d['cyqtr'], format="%Y%m%d"))
  
        df.columns = column_names
        if len(fdata) > 0:
          fdata = fdata.merge(df, how='outer', left_index=True, right_index=True)
        else:
          fdata = df
    for missing in missing_column_names:
      fdata[missing] = np.nan
    fdata = fdata[all_column_names]

    fdata = fdata[(fdata.index >= self._start.to_datetime()) & (fdata.index <= self._end.to_datetime())]
    return fdata

  def audit(self,n):
    print("auditing not yet available in python - see the R package")
    return

    if self._full is not True:
      raise Exception

    pass



def fn(qkids,
       items,
       qkid_items=None,
       start=20000101,
       end=today(),
       asof=today(),
       asfiled=False,
       aspit=False,
       ticker=True,
       full=False,
       cache=True
    ):
  """
  Functions to get 'as-reported' and 'revised'fundamental line item data from QK/Fundamentals API.

  Params
  ______

  qkids: qkid object constructed using `ticker`, `figi` or similar functions.
         See `help(qkid)` for information.

  items: a list of item codes coresponding to reporting concepts.

  qkid_items: alternate way to specify qkids and items created by `qkiditems` function

  start: date of returned series

  end: date of returned series

  asof: a number in form of YYYYMMDD. return last know values (including restatements) 
        for all prior periods `asof` this data. See details for more information on subscription limits

  asfiled: return original data values for all points

  aspit: requests full point-in-time table for historical dates. ONLY AVAILABLE TO ENTERPRISE.
         By default this is attempted once and if not enabled either the _latest_ 
         point-in-time or as-filed data returned depening on `asof`
         or `asfiled` argument values.

  ticker: should column names use tickers


  Details
  _______

  For each item in items requested a request applied to every qkid in
  qkids. All responses are cached by default. This can be disabled using cache=False.
  
  For enterprise subscriptions, if view='pit' is requested the subsequent object may
  contain restated and as-filed values and times. Two methods are provided to resolve 
  to unique observations at each date: `.asfiled()` converts the series to only include the
  initial observation recorded, whereas `.asof()` reconciles restatements up to
  and including the `date` specified. 


  Examples
  ________


  # Nvidia and Amazon revenues and net income
  >>> x = qk.fn(qk.ticker(["NVDA","AMZN"]),["SALE","NI"])

  # fiscal year to date, as of today, as a Pandas DataFrame
  >>> x.asof().start(20220101).end(20231231).to_df()

  # fiscal quarter, as-filed, as a Pandas DataFrame
  >>> x.asof().to_df()

  """

  from .qkid import cik

  view = "asof"
  if aspit is True:
    view = "pit"
  if asfiled is True:
    view = "asfiled"

  if qkid_items == None:
    qkid_items = qkiditems(qkids, items)

  fd = _FD(qkid_items, view, cache)

  #if full is True:
  #  return fd

  data = fd['data']
  return _Fn(data=data, elapsed=fd['elapsed'], view=view, start=start, end=end, ticker=ticker, asof=asof, resps=fd["resps"], qkid_items=qkid_items, full=full)

__QKAPIDATA = {'FD':{'pit':{},'asof':{},'asfiled':{}}}

def _FD(qkid_items, view, cache=False):
  stime = time.time()

  if type(view) is not list: view = [view]
  view = view[0]

  data = {}
  arg_id_item = ",".join(qkid_items["id"])

  apiKey = get_apikey()
  data = {}

  if cache is True:
    arg_id_item = []
    for qkid_item in qkid_items['id']:
      qkid_item = qkid_item.split(".")
      idKey = "CIK{0:010d}".format(int(qkid_item[0]))
      if idKey in __QKAPIDATA['FD'][view] and qkid_item[1] in __QKAPIDATA['FD'][view][idKey]:
        if idKey not in data:
          data[idKey] = {}
        data[idKey][qkid_item[1]] = __QKAPIDATA['FD'][view][idKey][qkid_item[1]]
      else:
        arg_id_item.append(".".join(qkid_item))

    arg_id_item = ",".join(arg_id_item)

  resps = []
  if len(arg_id_item) > 0:
    req = "https://api.qkiosk.io/data/fundamental"
    resp = requests.post(req, json={"apiKey":apiKey,"id_item":arg_id_item,"view":view})
    if resp.status_code != 200:
        raise ValueError("error: unable to complete request")

    content_list = []
    id_item = []
    resps = [resp]

    urls = resp.json()['Urls']
    fd = []

    def read_csv(url):
      r = requests.get(url)
      #resps.append(r)
      if r.status_code == 200:
        urlData = r.content
        rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
      else:
        rawData = pd.DataFrame()

      content = {"res":r,"data":rawData,"url":url,"id_item":re.sub(".*/fundamental/.*?/[a-z]+?/(.*?)/(CIK[0-9]{10}).*", "\\2,\\1", r.url)}
      fd.append(content)

    with concurrent.futures.ThreadPoolExecutor() as executor:
      executor.map(read_csv, urls)


    idItem = resp.json()['IdItem']
    idItems_id = [i['Id'].lstrip("0") for i in idItem]
    idItems_item = [i['Item'].lstrip("0") for i in idItem]

    #breakpoint()
    for i in [resp.json()["Urls"].index(x['url']) for x in fd]:
      idKey, idItems_item_i = fd[i]["id_item"].split(",")
      if idKey not in __QKAPIDATA['FD'][view]:
        __QKAPIDATA['FD'][view][idKey] = {}
      if idKey not in data:
        data[idKey] = {}

      __QKAPIDATA['FD'][view][idKey][idItems_item_i] = fd[i]['data']
      data[idKey][idItems_item_i] = fd[i]['data']


  elapsed = time.time() - stime
  fd = {"data":data,"view":view,"elapsed":elapsed,"resps":resps}

  return fd

def qkiditems(qkids, items):
  """

  """
  if type(items) is not list: items = [items]

  id_items = ["{}.{}".format(entity,item) for entity in qkids.entity for item in items]
  cik_entities = ["CIK{0:010d}".format(int(qkid)) for qkid in qkids.entity]
  data_items = {}
  for qkid in qkids.entity:
    data_items["CIK{0:010d}".format(int(qkid))] = items

  return {"id":id_items, "data":data_items}
