import io, re, time
import requests
import pandas as pd
import concurrent.futures
from .yyyymmdd import qtrsback
from .account import get_apikey

_NUM_THREADS = 5

class _Holders:
  def __init__(self, data, urls, resps=[], asof=True, asfiled=False):
    self.data = data
    self._urls = urls
    self._resps = resps
    self.full = True

    self.keep = "last"
    if asfiled is True:
      self.keep = "first"

  def asof(self, inplace=False):
    """ Return latest filed values (Not implemented)

    """
    if inplace is False:
        return _Holders(self.data, self._urls, asof=True, asfiled=False)

    self.keep = "last"
    return self

  def asfiled(self, inplace=False):
    """ Return first filed values (Not implemented)

    """
    if inplace is False:
        return _Holders(self.data, self._urls, asof=False, asfiled=True)

    self.keep = "first"
    return self

  def to_df(self, ascending=False, full=False):
    """ Convert To Panda's DataFrame

    """
    df = pd.concat(self.data)
    if self.full is True:
      return df

    df = df.sort_values(by=['filedDate'], ascending=[True]).drop_duplicates('filerCik',keep=self.keep)
    df = df.sort_values(by=['value'], ascending=[ascending]).reset_index(drop=True)
    return df

def holders(qkid, yyyyqq, qtrs=1):

  to_from = qtrsback(yyyyqq, qtrs)
  yyyy = ["{0:04d}".format(int(yyyyqq / 100)) for yyyyqq in to_from]
  qq = ["{0:02d}".format(yyyyqq % 100) for yyyyqq in to_from]

  ciks = qkid.entity
  tickers= qkid.to_ticker()

  holders = []
  resps = []

  def read_csv(url):
    r = requests.get(url)
    resps.append(r)
    if r.status_code == 200:
      urlData = r.content
      data = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
    else:
      data = pd.DataFrame()

    holders.append(data)

  apiKey = get_apikey()
  urls = []
  for cik in ciks:
    for y in yyyy:
      for q in qq:
        urls.append('https://api.qkiosk.io/data/instrument?apiKey={}&id={}&yyyy={}&qq={}'.format(apiKey,cik,y,q))

  with concurrent.futures.ThreadPoolExecutor(max_workers=_NUM_THREADS) as executor:
    executor.map(read_csv, urls)

  return _Holders(holders, urls, resps=resps)


class _Institutional:
  def __init__(self, data, qkid, yyyyqq, qtrs):
    self.qkid = qkid
    self.yyyyqq = yyyyqq
    self.qtrs = qtrs
    self.data = data

  def to_df(self):
    return pd.concat(self.data)

  def __repr__(self):
    return "Institutional:"

def institutional(qkid, yyyyqq, qtrs=1, agg=True):
  """
  Institutional Ownership

  Query all holdings by institutional asset manager or
  by instrument across managers.

  Parameters
  ----------

  qkid: the QKID of reporting institution

  yyyyqq: year and qtr of period reporting for

  qtrs: number of previous quarters to include

  agg: True - all other managers reporting are rolled up into one record
       False - shows possible other managers on separate lines.

  Details
  -------
  Depending on the aggregation requested 'aggType' the result will contain different fields. See the example
  package data 'sgcap' and 'deshaw' for specifics as well as details on what fields are.

  Returns
  _______

  And object of class Institutional

  Examples
  ________
  
  >>> citadel = qkiosk.search_mgr('citadel')
  >>> citadel_h = qkiosk.institutional(citadel, yyyyqq=202302)
  >>> citadel_h.to_df()

  """
  apiKey = get_apikey()

  to_from = qtrsback(yyyyqq, qtrs)
  yyyy = ["{0:04d}".format(int(yyyyqq / 100)) for yyyyqq in to_from]
  qq = ["{0:02d}".format(yyyyqq % 100) for yyyyqq in to_from]
  aggType = "a"
  if agg is not True:
    aggType = "n"

  cik = qkid.entity[0]

  holdings = []
  def read_csv(url):
    print("downloading {}".format(url.replace(apiKey,"XXXXXX")))
    holdings.append(pd.read_csv(url))

  urls = []
  for i in range(len(to_from)):
      urls.append('https://api.qkiosk.io/data/ownership?apiKey={}&ids={}&aggType={}&yyyy={}&qq={}&by=filing&retType=csv'.format(apiKey,cik,aggType,yyyy[i],qq[i]))

  s = 0
  for url in urls:
    read_csv(url)
    time.sleep(s)
    s = 0.02

  return _Institutional(holdings, qkid, yyyyqq, qtrs)


class _Insider(_Institutional):
  pass

def insider(qkid, yyyyqq, qtrs=1, form=['345','144']):
  """
  Insider Ownership

  Query all holdings by institutional asset manager or
  by instrument across managers.

  Parameters
  ----------

  qkid: the QKID of reporting institution

  yyyyqq: year and qtr of period reporting for

  qtrs: number of previous quarters to include

  form: filing type - 345 (form 3,4,5 officers, directors or 10% owners) or 144 (intent to sell)

  Details
  -------

  Returns
  _______

  And object of class Insider

  Examples
  ________
  
  >>> import qkiosk as qk
  >>> adm_i = qk.insider(qk.ticker("ADM"), yyyyqq=202302)
  >>> adm_i.to_df()

  """
  apiKey = get_apikey()

  to_from = qtrsback(yyyyqq, qtrs)
  yyyy = ["{0:04d}".format(int(yyyyqq / 100)) for yyyyqq in to_from]
  qq = ["{0:02d}".format(yyyyqq % 100) for yyyyqq in to_from]
  form = form[0]

  cik = qkid.entity[0]

  holdings = []
  def read_csv(url):
    print("downloading {}".format(url.replace(apiKey,"XXXXXX")))
    holdings.append(pd.read_csv(url))

  urls = []
  for i in range(len(to_from)):
      urls.append('https://api.qkiosk.io/data/ownership?apiKey={}&form={}&ids={}&yyyy={}&qq={}&by=filing&retType=csv'.format(apiKey,form,cik,yyyy[i],qq[i]))

  for url in urls:
    read_csv(url)
    time.sleep(0.10)

  return _Insider(holdings, qkid, yyyyqq, qtrs)

class _Beneficial(_Institutional):
  pass

def beneficial(qkid, yyyyqq, qtrs=1, form=['13D13G','13G','13D']):
  """
  Beneficial Ownership (Block Holders)

  All owners of 5% or more of a company are required to report thier
  holdings and subsequent changes to the SEC. These are reported in
  two forms - one for passive investors (13G) and one for those
  often termed activist, who are intending to exert control over management
  of the company. (13D)

  Parameters
  ----------

  qkid: the id of reporting institution or person, using qkid class

  yyyyqq: year and qtr of period reporting for

  qtrs: number of previous quarters to include

  form: filing type - 13D13G (all beneficial (5%) filers), 13G (non-activist), 13D (activist only)

  Details
  -------

  Returns
  _______

  And object of class Beneficial

  Examples
  ________
  
  >>> import qkiosk as qk
  >>> adm_i = qk.beneficial(qk.ticker("ADM"), yyyyqq=202302)
  >>> adm_i.to_df()

  """
  apiKey = get_apikey()

  to_from = qtrsback(yyyyqq, qtrs)
  yyyy = ["{0:04d}".format(int(yyyyqq / 100)) for yyyyqq in to_from]
  qq = ["{0:02d}".format(yyyyqq % 100) for yyyyqq in to_from]
  form = form[0]

  cik = qkid.entity[0]

  holdings = []
  def read_csv(url):
    print("downloading {}".format(url.replace(apiKey,"XXXXXX")))
    holdings.append(pd.read_csv(url))

  urls = []
  for i in range(len(to_from)):
      urls.append('https://api.qkiosk.io/data/ownership?apiKey={}&form={}&ids={}&yyyy={}&qq={}&by=filing&retType=csv'.format(apiKey,form,cik,yyyy[i],qq[i]))

  for url in urls:
    read_csv(url)
    time.sleep(0.10)

  return _Beneficial(holdings, qkid, yyyyqq, qtrs)

