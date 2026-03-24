"""Enum types for the IBM DataStage API."""

from enum import IntEnum, IntFlag, StrEnum


class CustInfoType(IntEnum):
    """Maps `infoType` values from `DSCUSTINFO`."""

    VALUE = 1
    DESCRIPTION = 2


class EnvVarType(StrEnum):
    """Maps `varType` values from `DSAddEnvVar`."""

    STRING = "String"
    ENCRYPTED = "Encrypted"


class JobInfoType(IntEnum):
    """Maps `infoType` values from `DSJOBINFO`."""

    STATUS = 1
    NAME = 2
    CONTROLLER = 3
    START_TIMESTAMP = 4
    WAVE_NUMBER = 5
    PARAMETER_LIST = 6
    STAGE_LIST = 7
    USER_STATUS = 8
    CONTROL = 9
    PID = 10
    LAST_TIMESTAMP = 11
    INVOCATIONS = 12
    INTERIM_STATUS = 13
    INVOCATION_ID = 14
    DESCRIPTION = 15
    STAGE_LIST2 = 16
    ELAPSED = 17
    EOT_COUNT = 18
    EOT_TIMESTAMP = 19
    DMI_SERVICE = 20
    MULTI_INVOKABLE = 21
    FULL_DESCRIPTION = 22
    RESTARTABLE = 24


class JobStatus(IntEnum):
    """Maps `jobStatus` values from `DSJOBINFO`."""

    RUNNING = 0
    RUN_OK = 1
    RUN_WARN = 2
    RUN_FAILED = 3
    QUEUED = 4
    VAL_OK = 11
    VAL_WARN = 12
    VAL_FAILED = 13
    RESET = 21
    CRASHED = 96
    STOPPED = 97
    NOT_RUNNABLE = 98
    NOT_RUNNING = 99


class LimitType(IntEnum):
    """Maps `limitType` values from `DSSetJobLimit`."""

    WARN = 1
    ROWS = 2


class LinkInfoType(IntEnum):
    """Maps `infoType` values from `DSLINKINFO`."""

    LAST_ERROR = 1
    NAME = 2
    ROW_COUNT = 3
    SQL_STATE = 4
    DBMS_CODE = 5
    DESCRIPTION = 6
    STAGE = 7
    INSTANCE_ROW_COUNT = 8
    EOT_ROW_COUNT = 9
    EXT_ROW_COUNT = 10


class LogEventType(IntEnum):
    """Maps `eventType` values from `DSLOGDETAILFULL`."""

    INFO = 1
    WARNING = 2
    FATAL = 3
    REJECT = 4
    STARTED = 5
    RESET = 6
    BATCH = 7
    OTHER = 98
    ANY = 99


class ParamType(IntEnum):
    """Maps `paramType` values from `DSPARAM`."""

    STRING = 0
    ENCRYPTED = 1
    INTEGER = 2
    FLOAT = 3
    PATHNAME = 4
    LIST = 5
    DATE = 6
    TIME = 7


class ProjectInfoType(IntEnum):
    """Maps `infoType` values from `DSPROJECTINFO`."""

    JOB_LIST = 1
    NAME = 2
    HOSTNAME = 3
    INSTALL_TAG = 4
    TCP_PORT = 5
    PATH = 6


class ProjectProperty(StrEnum):
    """Maps `property` values from `DSSetProjectProperty`."""

    OSH_VISIBLE_FLAG = "OSHVisibleFlag"
    JOB_ADMIN_ENABLED = "JobAdminEnabled"
    RTCP_ENABLED = "RTCPEnabled"
    PROTECTION_ENABLED = "ProtectionEnabled"
    PX_ADVANCED_RUNTIME_OPTS = "PXAdvRTOptions"
    PX_DEPLOY_CUSTOM_ACTION = "PXDeployCustomAction"
    PX_DEPLOY_JOB_DIR_TEMPLATE = "PXDeployJobDirectoryTemplate"
    PX_BASE_DIR = "PXRemoteBaseDirectory"
    PX_DEPLOY_GENERATE_XML = "PXDeployGenerateXML"


class ReportType(IntEnum):
    """Maps `reportType` values from `DSREPORTINFO`."""

    BASIC = 0
    DETAIL = 1
    XML = 2


class ReposJobFilter(IntFlag):
    """Maps `infoType` values from `DSREPOSINFO`."""

    SERVER = 1
    PARALLEL = 2
    MAINFRAME = 4
    SEQUENCE = 8
    ALL = 15


class ReposObjectType(IntEnum):
    """Maps `infoType` values from `DSREPOSINFO`."""

    JOBS = 1


class ReposRelationshipType(IntEnum):
    """Maps `relationshipType` values from `DSREPOSUSAGEJOB`."""

    JOB_USES_JOB = 1
    JOB_USED_BY_JOB = 2
    JOB_HAS_SOURCE_TABLE_DEF = 3
    JOB_HAS_TARGET_TABLE_DEF = 4
    JOB_HAS_SOURCE_OR_TARGET_TABLE_DEF = 5


class RunMode(IntEnum):
    """Maps `runMode` values from `DSRUNJOB`."""

    NORMAL = 1
    RESET = 2
    VALIDATE = 3
    RESTART = 4


class StageInfoType(IntEnum):
    """Maps `infoType` values from `DSSTAGEINFO`."""

    LINK_LIST = 1
    LAST_ERROR = 2
    NAME = 3
    TYPE = 4
    IN_ROW_NUM = 5
    VARIABLE_LIST = 6
    START_TIMESTAMP = 7
    END_TIMESTAMP = 8
    DESCRIPTION = 9
    INSTANCES = 10
    CPU = 11
    LINK_TYPES = 12
    ELAPSED = 13
    PID = 14
    STATUS = 15
    EOT_COUNT = 16
    EOT_TIMESTAMP = 17
    CUST_INFO_LIST = 18


class VarInfoType(IntEnum):
    """Maps `infoType` values from `DSVARINFO`."""

    VALUE = 1
    DESCRIPTION = 2
