"""
qkiosk: Interace to QUANTkiosk API

www.quantkiosk.com

"""

from .account import account, get_apikey, set_apikey
from .ownership import institutional, holders, insider, beneficial
from .fundamentals import fn, qkiditems, fncodes
from .qkid import qkid, ticker, cik, figi, name, fundname, search_co, search_mgr
from .qkid import jw, jaro_winkler, menu, search
from .univ import univ
from .utils import digits

from .yyyymmdd import yyyymmdd, today, is_yyyymmdd, qtrs, days, seq_yyyymmdd
from .data import load_deshaw, load_sgcap, load_crox, load_nke, load_pfe, load_pershing, data
