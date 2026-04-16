from .qkid import __reqQKID, _Qkid
from .yyyymmdd import today

_QKID_UNIV = {}

def univ(univ, dt=today(), src="QK", cache=True):
    if cache and univ in _QKID_UNIV:
        return _QKID_UNIV[univ]

    if src == "QK":
        src = "univ/QK"
        u = __reqQKID(src+"/"+univ+"/"+univ)
        u = u["qkid"].to_list()
    else:
        return None

    u = _Qkid(u)
    _QKID_UNIV[univ] = u

    return u
