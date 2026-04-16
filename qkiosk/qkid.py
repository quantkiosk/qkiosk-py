from .account import get_apikey
from .utils import is_documented_by
from .yyyymmdd import yyyymmdd, today

import requests
import pandas as pd
import numpy as np
import pprint as pp

_QKID_MAP = {}

def jw(st1, st2):
    """
    Compute Jaro-Winkler distance between two strings.
    """
    if len(st1) < len(st2):
        st1, st2 = st2, st1
    len1, len2 = len(st1), len(st2)
    if len2 == 0:
        return 0.0
    delta = max(0, len2 // 2 - 1)
    flag = [False for _ in range(len2)]  # flags for possible transpositions
    ch1_match = []
    for idx1, ch1 in enumerate(st1):
        for idx2, ch2 in enumerate(st2):
            if idx2 <= idx1 + delta and idx2 >= idx1 - delta and ch1 == ch2 and not flag[idx2]:
                flag[idx2] = True
                ch1_match.append(ch1)
                break

    matches = len(ch1_match)
    if matches == 0:
        return 1.0
    transpositions, idx1 = 0, 0
    for idx2, ch2 in enumerate(st2):
        if flag[idx2]:
            transpositions += (ch2 != ch1_match[idx1])
            idx1 += 1

    jaro = (matches / len1 + matches / len2 + (matches - transpositions/2) / matches) / 3.0
    commonprefix = 0
    for i in range(min(4, len2)):
        commonprefix += (st1[i] == st2[i])

    return 1.0 - (jaro + commonprefix * 0.1 * (1 - jaro))

def jaro_distance(s1, s2):
    s1_len = len(s1)
    s2_len = len(s2)

    if s1_len == 0 or s2_len == 0:
        return 0.0

    match_distance = max(s1_len, s2_len) // 2 - 1

    s1_matches = [False] * s1_len
    s2_matches = [False] * s2_len

    matches = 0
    transpositions = 0

    # Finding matches
    for i in range(s1_len):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, s2_len)

        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    k = 0
    for i in range(s1_len):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    transpositions /= 2

    return (matches / s1_len + matches / s2_len + (matches - transpositions) / matches) / 3.0

def jaro_winkler(s1, s2, p=0.1, max_l=4):
    jaro_dist = jaro_distance(s1, s2)

    # Find the length of common prefix up to a max of max_l
    prefix_length = 0
    for i in range(min(len(s1), len(s2))):
        if s1[i] == s2[i]:
            prefix_length += 1
        else:
            break
        if prefix_length == max_l:
            break

    return jaro_dist + (prefix_length * p * (1 - jaro_dist))

def search(x, type=['issuer','manager','fund','person'], n=10):
  if type == "issuer": 
    _load_mapping("name")
    nm = _QKID_MAP['name']['name'].keys()
    dist = [1-jaro_winkler(x.upper(),nm.upper()) for nm in nm]
    matches = np.array(list(nm))[np.argsort(np.array(dist))[range(n)]]
    return name(matches.tolist())
  elif type == "manager":
    _load_mapping("fund")
    nm = _QKID_MAP['fund']['fund'].keys()
    dist = [1-jaro_winkler(x.upper(),nm.upper()) for nm in nm]
    matches = np.array(list(nm))[np.argsort(np.array(dist))[range(n)]]
    return fundname(matches.tolist())

  return None

  

def menu(choices,title):
  print("")
  [print(str(i+1).rjust(len(str(len(choices))),' ')+". "+e) for i,e in enumerate(choices)] 
  return input("\nSelection: ")
  

class _Qkid:
  """

## QKID Tools

### Description

Functions to create, extract and convert entity and instrument
identifiers within QUANTkiosk's QKID open symbology.

To facilitate discovery, qkiosk provides search functionality.
`qk_search_co` offers fuzzy matching to public companies (e.g. Pfizer or McDonalds),
returning a menu to select the match from. The return value is the matched `QKID`.
Similar functionality is available to find investment managers (e.g. D.E Shaw) via 
the `qk_search_mgr` function.


### Usage

classname(qkid)
detail(qkid)

qkid.entity
qkid.cls
qkid.instrument

## ticker conversion 
  ticker(ticker, ...)    # ticker -> qkid
  qkid.to_ticker()       # qkid -> ticker

## figi string to qkid object
  figi(figi, type = c("figi", "shareClass", "composite"), ...)

## qkid object to figi string
  qkid.to_figi(type = c("figi", "shareClass", "composite"), ...)

## cik conversion
  cik(cik, ...)          # cik -> qkid
  qkid.to_cik()          # qkid -> cik

permid(permid, type = c("org", "instrument", "quote"), ...)
to_permid(qkid, type = c("org", "instrument", "quote"), ...)

name(name, ...)
as_name(qkid, ...)

# custom constructor
qkid(qkid, src="qkid", srcid=qkid, retrieved=yyyymmdd())

### Arguments

### Examples
ticker("AAPL")
ticker(["HD","LOW"])

  """
  def __init__(self, qkid, src='qkid', srcid=None, retrieved=today()):
    if type(qkid) is not list: qkid = [qkid]
    self.qkid = qkid
    self.src = src
    if srcid is None:
        srcid = qkid
    if type(srcid) is not list: srcid = [srcid]
    self.srcid = srcid
    self.retrieved = retrieved

  def __repr__(self):
    return "qkid: {}".format(pp.pformat(self.qkid, sort_dicts=False))

  def __getitem__(self, item):
    qkid = self.qkid[item]
    srcid = self.srcid
    return _Qkid(qkid,self.src,srcid)

  def __len__(self):
    return len(self.qkid)

  @property
  def entity(self):
    qkid = self.qkid
    if type(qkid) is not list: qkid = [qkid]
    return [q[:10] for q in qkid]

  @property
  def cls(self):
    qkid = self.qkid
    if type(qkid) is not list: qkid = [qkid]
    return [q[11:15] for q in qkid]

  @property
  def instrument(self):
    qkid = self.qkid
    if type(qkid) is not list: qkid = [qkid]
    return [q[16:] for q in qkid]

  def to_ticker(self, cache=None):
    __doc__ = _Qkid.__doc__
    x = self.qkid
    _load_mapping('ticker', cache=cache)
    if type(x) is not list: x = [x]
    ticker = [_QKID_MAP['ticker']['qkid'][id] if id in _QKID_MAP['ticker']['qkid'] else None for id in x]
    return ticker

  def to_figi(self, cache=None):
    __doc__ = _Qkid.__doc__
    x = self.qkid
    _load_mapping('figi', cache=cache)
    if type(x) is not list: x = [x]
    figi = [_QKID_MAP['figi']['qkid'][id] if id in _QKID_MAP['figi']['qkid'] else None for id in x]
    return figi

  def to_name(self, cache=None):
    __doc__ = _Qkid.__doc__
    x = self.qkid
    _load_mapping('name', cache=cache)
    if type(x) is not list: x = [x]
    figi = [_QKID_MAP['name']['qkid'][id] if id in _QKID_MAP['name']['qkid'] else None for id in x]
    return figi

  def to_cik(qkid, zeros=False):
    __doc__ = _Qkid.__doc__
    x = qkid.qkid
    _load_mapping('cik')
    if type(x) is not list: x = [x]
    cik = [_QKID_MAP['cik']['qkid'][id] if id in _QKID_MAP['cik']['qkid'] else None for id in x]
    if not zeros:
      cik = [cik.lstrip("0") for cik in cik]
    return cik

@is_documented_by(_Qkid)
def search_co(x, n=10):
  choices = search(x, 'issuer', n=n)
  choice = menu(choices.srcid,"")
  if choice == '':
    return None
  choice = int(choice)-1
  if choice < 0 or choice > len(choices):
    return None
  return choices[choice]

@is_documented_by(_Qkid)
def search_mgr(x, n=10):
  choices = search(x, 'manager', n=n)
  choice = menu(choices.srcid,"")
  if choice == '':
    return None
  choice = int(choice)-1
  if choice < 0 or choice > len(choices):
    return None
  return choices[choice]



def _load_mapping(x, cache=None):
    if x not in _QKID_MAP:
        mapping = __reqQKID(x)
        qkids = mapping['qkid'].tolist()
        values = mapping[x].tolist()
        qkid_value = {qkids: values for qkids,values in zip(qkids,values)}
        #value_qkid = {qkids: values for qkids,values in zip(values,qkids)}
        value_qkid = {values: qkids for values,qkids in zip(values,qkids) if qkids[14] == '0'}
        _QKID_MAP[x] = {'qkid':qkid_value,x:value_qkid}

@is_documented_by(_Qkid)
def qkid(qkid, src = "qkid", srcid=None, retrieved = yyyymmdd()):
    if type(qkid) is list:
        print("qkid is a list")

    if srcid is None:
        srcid = qkid

    return _Qkid(qkid, src, srcid, retrieved)

@is_documented_by(_Qkid)
def ticker(x, cache=None):
    _load_mapping('ticker', cache=cache)
    if type(x) is not list: x = [x]
    qkid = [_QKID_MAP['ticker']['ticker'][id] if id in _QKID_MAP['ticker']['ticker'] else None for id in x]
    return _Qkid(qkid,'ticker',srcid=x)

@is_documented_by(_Qkid)
def figi(x, cache=None):
    _load_mapping('figi', cache=cache)
    if type(x) is not list: x = [x]
    qkid = [_QKID_MAP['figi']['figi'][id] if id in _QKID_MAP['figi']['figi'] else None for id in x]
    return _Qkid(qkid,'figi',srcid=x)

@is_documented_by(_Qkid)
def cik(x, cache=None):
    _load_mapping('cik', cache=cache)
    if type(x) is not list: x = [x]
    qkid = [_QKID_MAP['cik']['cik']["{0:0d}".format(int(id))] if "{0:0d}".format(int(id)) in _QKID_MAP['cik']['cik'] else "{}.0000.000000000".format("{0:0d}".format(id).zfill(10)) for id in x]
    return _Qkid(qkid,'cik',srcid=x)

@is_documented_by(_Qkid)
def name(x, cache=None):
    _load_mapping('name', cache=cache)
    if type(x) is not list: x = [x]
    qkid = [_QKID_MAP['name']['name'][id] if id in _QKID_MAP['name']['name'] else None for id in x]
    return _Qkid(qkid,'name',srcid=x)

@is_documented_by(_Qkid)
def fundname(x, cache=None):
    _load_mapping('fund', cache=cache)
    if type(x) is not list: x = [x]
    qkid = [_QKID_MAP['fund']['fund'][id] if id in _QKID_MAP['fund']['fund'] else None for id in x]
    return _Qkid(qkid,'fund',srcid=x)

def __reqQKID(id):
    apiKey = get_apikey()

    req = "https://api.qkiosk.io/data/qkid"
    resp = requests.post(req, json={"apiKey":apiKey,"ids":id})
    return pd.read_csv(resp.json()["Urls"][0], dtype=str)
