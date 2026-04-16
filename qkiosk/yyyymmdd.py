from datetime import date, datetime, timedelta
from .utils import is_documented_by
from numpy import array, cumsum
import os



class YYYYMMDD:
    """
    Simplified Dates

    Simplified dates expressed as integers to facilitate easy API access.

    Parameters
    __________


    Details
    _______


    Examples
    ________


    """
    def __init__(self, x=19700101, tz=os.getenv("TZ")):
        self.tz = tz
        if tz == "":
            self.tz = "UTC"
        if type(x) == int:
            if len(str(x)) == 8:
                self.date = x
            else:
                raise ValueError("initial value must be either 8 digit integer of form yyyymmdd or a datetime object")
        else:
            self.date = int(x.strftime("%Y%m%d"))
        self.date = self.date


    def __add__(self, days):
        if type(days) is range or type(days) is list:
            return [self + i for i in days]
        days_duration = timedelta(days=days)
        year = int(self.date / 10000)
        month = int((self.date % 10000) / 100)
        day = int(self.date % 100)

        return YYYYMMDD(date(year,month,day) + days_duration)

    def __sub__(self, days):
        days_duration = timedelta(days=days)
        year = int(self.date / 10000)
        month = int((self.date % 10000) / 100)
        day = int(self.date % 100)

        return YYYYMMDD(date(year,month,day) - days_duration)

    def __repr__(self):
        return str(self.date)

    def to_qq(self):
        qq = int((int((self.date % 10000) / 100)-1) / 3) + 1
        return qq

    def to_yyyy(self):
        yyyy = int(self.date / 10000)
        return yyyy

    def to_yyyyqq(self):
        yyyyqq = self.to_yyyy() * 100 + self.to_qq()
        return yyyyqq
         
    def to_int(self):
        return self.date

    def to_date(self):
        year = int(self.date / 10000)
        month = int((self.date % 10000) / 100)
        day = int(self.date % 100)
        return date(year,month,day)

    def to_datetime(self):
        year = int(self.date / 10000)
        month = int((self.date % 10000) / 100)
        day = int(self.date % 100)
        return datetime(year,month,day)

    def diff(self):
        pass

@is_documented_by(YYYYMMDD)
def seq_yyyymmdd(start, end, length_out=None):
    start = yyyymmdd(start).to_date()
    if end is not None and length_out is None:
       length_out = (yyyymmdd(end).to_date() - start).days
    dates = [start] + [start + timedelta(days=x+1) for x in range(length_out)]
    return [yyyymmdd(int(x.strftime("%Y%m%d"))) for x in dates]


def is_yyyymmdd(x):
    if type(x) == YYYYMMDD:
        return True
    else:
        return False        

@is_documented_by(YYYYMMDD)
def today():
    return YYYYMMDD(int(datetime.today().strftime("%Y%m%d")))
        

@is_documented_by(YYYYMMDD)
def _yyyymmdd(yyyymmdd=19700101):
    if is_yyyymmdd(yyyymmdd):
        return yyyymmdd

    return YYYYMMDD(yyyymmdd)

@is_documented_by(YYYYMMDD)
def yyyymmdd(yyyymmdd=today()):
    if is_yyyymmdd(yyyymmdd):
      return yyyymmdd
    year = int(yyyymmdd / 10000)
    month = int((yyyymmdd % 10000) / 100)
    day = int(yyyymmdd % 100)

    return YYYYMMDD(date(year, month, day))

def qtrs(n):
    return int(n) * 91

def days(n):
    return int(n)

def qtrsback(yyyyqq, N=1):
    if len(str(yyyyqq)) == 4:
        yyyyqq = yyyyqq * 100
    if N == 1:
        return [yyyyqq]
    #z = [[4,1,2,3][(int(int(yyyyqq) / 100 - r + 1)  % 4)] for r in range(N-1)]
    z = [[4,1,2,3][((yyyyqq % 100) - (r + 1)) % 4] for r in range(N-1)]
    zz = [0] * (N-1)
    for i in [i for i,x in enumerate(z) if x==4]:
        zz[i] = -1

    return [yyyyqq] + [qq+yyyy for qq, yyyy in zip(z, [(int(yyyyqq / 100) + adj) * 100 for adj in cumsum(array(zz)).tolist()])]
