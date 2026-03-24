"""Data structures used in the IBM DataStage API."""

import platform
from ctypes import (
    POINTER,
    Structure,
    Union,
    c_char,
    c_char_p,
    c_float,
    c_int,
    c_ubyte,
    c_uint32,
    c_uint64,
)

time_t = c_uint32 if platform.system() == "Windows" else c_uint64


class DSPROJECT(Structure):
    _fields_ = [
        ("dsapiVersionNo", c_int),
        ("sessionId", c_int),
        ("valueMark", c_ubyte),
        ("fieldMark", c_ubyte),
    ]


class DSJOB(Structure):
    _fields_ = [
        ("hProject", POINTER(DSPROJECT)),
        ("serverJobHandle", c_char_p),
        ("logData", c_char_p),
        ("logDataLen", c_int),
        ("logDataPsn", c_int),
    ]


class _DSJOBINFO(Union):
    _fields_ = [
        ("jobStatus", c_int),
        ("jobController", c_char_p),
        ("jobStartTime", time_t),
        ("jobWaveNumber", c_int),
        ("userStatus", c_char_p),
        ("stageList", POINTER(c_char)),
        ("paramList", POINTER(c_char)),
        ("jobName", c_char_p),
        ("jobControl", c_int),
        ("jobPid", c_int),
        ("jobLastTime", time_t),
        ("jobInvocations", POINTER(c_char)),
        ("jobInterimStatus", c_int),
        ("jobInvocationId", c_char_p),
        ("jobDesc", c_char_p),
        ("stageList2", POINTER(c_char)),
        ("jobElapsed", c_char_p),
        ("jobDMIService", c_int),
        ("jobMultiInvokable", c_int),
        ("jobFullDesc", c_char_p),
        ("jobRestartable", c_int),
    ]


class DSJOBINFO(Structure):
    _fields_ = [
        ("infoType", c_int),
        ("info", _DSJOBINFO),
    ]


class _DSPROJECTINFO(Union):
    _fields_ = [
        ("jobList", POINTER(c_char)),
        ("projectName", c_char_p),
        ("projectPath", c_char_p),
        ("hostName", c_char_p),
        ("installTag", c_char_p),
        ("tcpPort", c_char_p),
    ]


class DSPROJECTINFO(Structure):
    _fields_ = [
        ("infoType", c_int),
        ("info", _DSPROJECTINFO),
    ]


class DSLOGEVENT(Structure):
    _fields_ = [
        ("eventId", c_int),
        ("timestamp", time_t),
        ("type", c_int),
        ("message", c_char_p),
    ]


class DSLOGDETAILFULL(Structure):
    _fields_ = [
        ("eventId", c_int),
        ("timestamp", time_t),
        ("type", c_int),
        ("username", c_char_p),
        ("fullMessage", POINTER(c_char)),
        ("messageId", c_char_p),
        ("invocationId", c_char_p),
    ]


class DSLOGDETAIL(Structure):
    _fields_ = [
        ("eventId", c_int),
        ("timestamp", time_t),
        ("type", c_int),
        ("username", c_char_p),
        ("fullMessage", POINTER(c_char)),
    ]


class _DSPARAM(Union):
    _fields_ = [
        ("pString", c_char_p),
        ("pEncrypt", c_char_p),
        ("pInt", c_int),
        ("pFloat", c_float),
        ("pPath", c_char_p),
        ("pListValue", c_char_p),
        ("pDate", c_char_p),
        ("pTime", c_char_p),
    ]


class DSPARAM(Structure):
    _fields_ = [
        ("paramType", c_int),
        ("paramValue", _DSPARAM),
    ]


class DSPARAMINFO(Structure):
    _fields_ = [
        ("defaultValue", DSPARAM),
        ("helpText", c_char_p),
        ("paramPrompt", c_char_p),
        ("paramType", c_int),
        ("desDefaultValue", DSPARAM),
        ("listValues", c_char_p),
        ("desListValues", c_char_p),
        ("promptAtRun", c_int),
    ]


class _DSREPORTINFO(Union):
    _fields_ = [("reportText", c_char_p)]


class DSREPORTINFO(Structure):
    _fields_ = [
        ("reportType", c_int),
        ("info", _DSREPORTINFO),
    ]


class DSREPOSUSAGEJOB(Structure):
    pass


DSREPOSUSAGEJOB._fields_ = [
    ("jobname", c_char_p),
    ("jobtype", c_int),
    ("nextjob", POINTER(DSREPOSUSAGEJOB)),
    ("childjob", POINTER(DSREPOSUSAGEJOB)),
]


class _DSREPOSUSAGE(Union):
    _fields_ = [("jobs", POINTER(DSREPOSUSAGEJOB))]


class DSREPOSUSAGE(Structure):
    _fields_ = [("infoType", c_int), ("info", _DSREPOSUSAGE)]


class DSREPOSJOBINFO(Structure):
    pass


DSREPOSJOBINFO._fields_ = [
    ("jobname", c_char_p),
    ("jobtype", c_int),
    ("nextjob", POINTER(DSREPOSJOBINFO)),
]


class _DSREPOSINFO(Union):
    _fields_ = [("jobs", POINTER(DSREPOSJOBINFO))]


class DSREPOSINFO(Structure):
    _fields_ = [
        ("infoType", c_int),
        ("info", _DSREPOSINFO),
    ]


class _DSSTAGEINFO(Union):
    _fields_ = [
        ("lastError", DSLOGDETAIL),
        ("typeName", c_char_p),
        ("inRowNum", c_int),
        ("linkList", POINTER(c_char)),
        ("stageName", c_char_p),
        ("varList", POINTER(c_char)),
        ("stageStartTime", time_t),
        ("stageEndTime", time_t),
        ("linkTypes", POINTER(c_char)),
        ("stageDesc", c_char_p),
        ("instList", POINTER(c_char)),
        ("cpuList", POINTER(c_char)),
        ("stageElapsed", c_char_p),
        ("pidList", POINTER(c_char)),
        ("stageStatus", c_int),
        ("custInfoList", POINTER(c_char)),
    ]


class DSSTAGEINFO(Structure):
    _fields_ = [
        ("infoType", c_int),
        ("info", _DSSTAGEINFO),
    ]


class _DSLINKINFO(Union):
    _fields_ = [
        ("lastError", DSLOGDETAIL),
        ("rowCount", c_int),
        ("linkName", c_char_p),
        ("linkSQLState", c_char_p),
        ("linkDBMSCode", c_char_p),
        ("linkDesc", c_char_p),
        ("linkedStage", c_char_p),
        ("rowCountList", POINTER(c_char)),
    ]


class DSLINKINFO(Structure):
    _fields_ = [
        ("infoType", c_int),
        ("info", _DSLINKINFO),
    ]


class _DSVARINFO(Union):
    _fields_ = [
        ("varValue", c_char_p),
        ("varDesc", c_char_p),
    ]


class DSVARINFO(Structure):
    _fields_ = [
        ("infoType", c_int),
        ("info", _DSVARINFO),
    ]


class _DSCUSTINFO(Union):
    _fields_ = [
        ("custInfoValue", c_char_p),
        ("custInfoDesc", c_char_p),
    ]


class DSCUSTINFO(Structure):
    _fields_ = [
        ("infoType", c_int),
        ("info", _DSCUSTINFO),
    ]
