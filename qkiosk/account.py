import os
import requests
import datetime

def get_apikey():
    return os.environ["QK_API_KEY"]

def set_apikey(apikey):
    os.environ["QK_API_KEY"] = str(apikey)

class _Account:
    def __init__(self, account):
        self.asof = account["AsOf"]
        self.usage = account["Usage"]
        self.quota = account["Quota"]
        self.hardquota = account["HardQuota"]
        self._datafiles = account["DataFiles"]
        self._univfiles = account["UnivFiles"]

    def __repr__(self):
        asof = datetime.datetime.strptime(self.asof, '%A, %d-%b-%y %H:%M:%S %Z')
        diff = datetime.datetime(asof.year, asof.month, asof.day+1) - asof
        hours = int(diff.seconds / 60 / 60)
        mins = int(diff.seconds / 60) - (int(diff.seconds / 60 / 60) * 60)

        account = """
QUANTkiosk Account: ( {} )

Daily Quota: {:d} ( Hard Quota: {:d} )
Daily Usage: {:d}

Daily quota resets in: {:d}h {:d}m

Visit https://quantkiosk.com/account to change your plan or explore offerings.
"""
        return account.format(self.asof, self.quota, self.hardquota, self.usage, hours, mins)

    @property
    def datafiles(self):
        return [data["File"] for data in self._datafiles]

    @property
    def univfiles(self):
        return [univ["File"] for univ in self._univfiles]

def account():
    apiKey = get_apikey()
    r = requests.get('https://api.qkiosk.io/account?apiKey='+apiKey)
    return _Account(r.json())
