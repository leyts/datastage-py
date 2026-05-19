"""Parameter wrappers and helpers for DataStage jobs."""

from dataclasses import dataclass, field
from datetime import date, time
from pathlib import PurePath

from datastage_py._constants import ParamType
from datastage_py._structures import DSPARAM
from datastage_py.utils import encode_string

type ParamValue = int | float | str | PurePath | date | time | Encrypted


@dataclass(frozen=True, slots=True)
class Encrypted:
    """An encrypted string parameter value."""

    value: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class JobParameter:
    name: str
    value: ParamValue

    @property
    def type(self) -> ParamType:
        match self.value:
            case Encrypted():
                result = ParamType.ENCRYPTED
            case PurePath():
                result = ParamType.PATHNAME
            case date():
                result = ParamType.DATE
            case time():
                result = ParamType.TIME
            case int():
                result = ParamType.INTEGER
            case float():
                result = ParamType.FLOAT
            case str():
                result = ParamType.STRING
        return result

    def to_param(self) -> DSPARAM:
        param = DSPARAM()
        param.paramType = self.type
        match self.value:
            case Encrypted(value=v):
                param.paramValue.pEncrypt = encode_string(v)
            case PurePath() as p:
                param.paramValue.pPath = encode_string(p.as_posix())
            case date() as d:
                param.paramValue.pDate = encode_string(d.isoformat())
            case time() as t:
                param.paramValue.pTime = encode_string(t.isoformat())
            case int() as i:
                param.paramValue.pInt = i
            case float() as f:
                param.paramValue.pFloat = f
            case str() as s:
                param.paramValue.pString = encode_string(s)
        return param
