"""
Datasets included in qkiosk package

"""
import os
import pandas as pd

from .qkid import ticker
from .utils import is_documented_by
from .fundamentals import _Fn, qkiditems

def data():
    """
	Data sets in ‘qkiosk’:

	crox        Crocs Institutional Holders Details By Issuer
	deshaw      D.E. Shaw Institutional Ownership Details (Including Submanagers)
	nke         Nike (NKE) Insider Ownership Data
	nvda_intent Nvidia (NVDA) Restricted or Control Shares Intention to Sell
	nvda_sales  Nvidia (NVDA) Restricted or Control Shares Sold
	pershing    Pershing Square Beneficial and Activist Details
	pfe         Pfizer (PFE) Revenue Data
	sgcap       SG Capital Institutional Ownership Details (Aggregated)

    e.g. load_pershing() loads as a Pandas DataFrame
    """

@is_documented_by(data)
def load_deshaw():
    location = os.path.dirname(os.path.realpath(__file__))
    deshaw_file = os.path.join(location, 'datasets', 'deshaw.csv')


    deshaw = pd.read_csv(deshaw_file)
    return deshaw

@is_documented_by(data)
def load_sgcap():
    location = os.path.dirname(os.path.realpath(__file__))
    sgcap_file = os.path.join(location, 'datasets', 'sgcap.csv')


    sgcap = pd.read_csv(sgcap_file)
    return sgcap

@is_documented_by(data)
def load_crox():
    location = os.path.dirname(os.path.realpath(__file__))
    crox_file = os.path.join(location, 'datasets', 'crox.csv')


    crox = pd.read_csv(crox_file)
    return crox

@is_documented_by(data)
def load_pershing():
    location = os.path.dirname(os.path.realpath(__file__))
    pershing_file = os.path.join(location, 'datasets', 'pershing.csv')


    pershing = pd.read_csv(pershing_file)
    return pershing


@is_documented_by(data)
def load_pfe():
    location = os.path.dirname(os.path.realpath(__file__))
    pfe_file = os.path.join(location, 'datasets', 'pfe.csv')


    pfe = pd.read_csv(pfe_file)
    qkid_items = qkiditems(ticker(["PFE"]),["SALE"])
    data = {'CIK0000078003': {'SALE':pfe}}
    pfe = _Fn(data, elapsed=0, view='asof',asof=True,qkid_items=qkid_items, full=False)
    return pfe


@is_documented_by(data)
def load_nke():
    location = os.path.dirname(os.path.realpath(__file__))
    nke_file = os.path.join(location, 'datasets', 'nke.csv')


    nke = pd.read_csv(nke_file)
    return nke
