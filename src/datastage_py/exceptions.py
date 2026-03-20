"""Error handling for the IBM DataStage API."""

from typing import NoReturn


class DSAPIError(Exception):
    """Base exception for all DataStage API errors."""

    code: int = -1
    token: str = ""
    default_msg: str = ""

    def __init__(
        self,
        func: str,
        msg: str = "",
        *,
        code: int | None = None,
    ) -> None:
        """Initialise the error with the failing function name and message."""
        self.func = func
        self.msg = msg or self.default_msg
        if code is not None:
            self.code = code
        super().__init__(f"{func}: {self.msg}")


class DSBadHandleError(DSAPIError):
    token = "DSJE_BADHANDLE"
    code = -1
    default_msg = "Invalid JobHandle"


class DSBadStateError(DSAPIError):
    token = "DSJE_BADSTATE"
    code = -2
    default_msg = "Job is not in the right state (compiled, not running)"


class DSBadParamError(DSAPIError):
    token = "DSJE_BADPARAM"
    code = -3
    default_msg = "ParamName is not a parameter name in the job"


class DSBadValueError(DSAPIError):
    token = "DSJE_BADVALUE"
    code = -4
    default_msg = (
        "LimitValue is not appropriate for the limiting condition type"
    )


class DSBadTypeError(DSAPIError):
    token = "DSJE_BADTYPE"
    code = -5
    default_msg = "Invalid EventType value"


class DSWrongJobError(DSAPIError):
    token = "DSJE_WRONGJOB"
    code = -6
    default_msg = "Job for this JobHandle was not started from a call to DSRunJob by the current process"


class DSBadStageError(DSAPIError):
    token = "DSJE_BADSTAGE"
    code = -7
    default_msg = "StageName does not refer to a known stage in the job"


class DSNotInStageError(DSAPIError):
    token = "DSJE_NOTINSTAGE"
    code = -8
    default_msg = "Internal engine error"


class DSBadLinkError(DSAPIError):
    token = "DSJE_BADLINK"
    code = -9
    default_msg = (
        "LinkName does not refer to a known link for the stage in question"
    )


class DSJobLockedError(DSAPIError):
    token = "DSJE_JOBLOCKED"
    code = -10
    default_msg = "The job is locked by another process"


class DSJobDeletedError(DSAPIError):
    token = "DSJE_JOBDELETED"
    code = -11
    default_msg = "The job has been deleted"


class DSBadNameError(DSAPIError):
    token = "DSJE_BADNAME"
    code = -12
    default_msg = "Job name badly formed"


class DSBadTimeError(DSAPIError):
    token = "DSJE_BADTIME"
    code = -13
    default_msg = "Timestamp parameter was badly formed"


class DSTimeoutError(DSAPIError):
    token = "DSJE_TIMEOUT"
    code = -14
    default_msg = "The job appears not to have started after waiting for a reasonable length of time (approx. 30 minutes)"


class DSDecryptError(DSAPIError):
    token = "DSJE_DECRYPTERR"
    code = -15
    default_msg = "Failed to decrypt encrypted values"


class DSNoAccessError(DSAPIError):
    token = "DSJE_NOACCESS"
    code = -16
    default_msg = "Cannot get values, default values, or design default values for any job except the current job (Job Handle == DSJ.ME)"


class DSNoTemplateError(DSAPIError):
    token = "DSJE_NOTEMPLATE"
    code = -17
    default_msg = "Cannot find template file"


class DSBadTemplateError(DSAPIError):
    token = "DSJE_BADTEMPLATE"
    code = -18
    default_msg = "Error encountered when processing template file"


class DSNoParamError(DSAPIError):
    token = "DSJE_NOPARAM"
    code = -19
    default_msg = (
        "Parameter name missing. Field does not look like 'name:value'"
    )


class DSNoFilePathError(DSAPIError):
    token = "DSJE_NOFILEPATH"
    code = -20
    default_msg = "File path name not given"


class DSCmdError(DSAPIError):
    token = "DSJE_CMDERROR"
    code = -21
    default_msg = "Error when executing external command"


class DSBadVarError(DSAPIError):
    token = "DSJE_BADVAR"
    code = -22
    default_msg = "VarName does not refer to a known variable in the job"


class DSNonUniqueIdError(DSAPIError):
    token = "DSJE_NONUNIQUEID"
    code = -23
    default_msg = "Id already exists for a job in this project"


class DSInvalidIdError(DSAPIError):
    token = "DSJE_INVALIDID"
    code = -24
    default_msg = "Invalid Job Id"


class DSInvalidQueueError(DSAPIError):
    token = "DSJE_INVALIDQUEUE"
    code = -25
    default_msg = "Invalid Queue"


class DSWLMDisabledError(DSAPIError):
    token = "DSJE_WLMDISABLED"
    code = -26
    default_msg = "WLM is not enabled"


class DSWLMNotRunningError(DSAPIError):
    token = "DSJE_WLMNOTRUNNING"
    code = -27
    default_msg = "WLM is not running"


class DSNoRolePermissionsError(DSAPIError):
    token = "DSJE_NOROLEPERMISSIONS"
    code = -28
    default_msg = "User does not have required role permissions to perform this operation"


class DSRepError(DSAPIError):
    token = "DSJE_REPERROR"
    code = -99
    default_msg = "General engine error"


class DSNotAdminUserError(DSAPIError):
    token = "DSJE_NOTADMINUSER"
    code = -100
    default_msg = "User is not an administrator"


class DSIsAdminFailedError(DSAPIError):
    token = "DSJE_ISADMINFAILED"
    code = -101
    default_msg = "Failed to determine whether user is an administrator"


class DSReadProjectPropertyError(DSAPIError):
    token = "DSJE_READPROJPROPERTY"
    code = -102
    default_msg = "Failed to read property"


class DSWriteProjectPropertyError(DSAPIError):
    token = "DSJE_WRITEPROJPROPERTY"
    code = -103
    default_msg = "Writing project properties failed"


class DSBadPropertyError(DSAPIError):
    token = "DSJE_BADPROPERTY"
    code = -104
    default_msg = "Unknown property name"


class DSPropertyNotSupportedError(DSAPIError):
    token = "DSJE_PROPNOTSUPPORTED"
    code = -105
    default_msg = "Unsupported property"


class DSBadPropertyValueError(DSAPIError):
    token = "DSJE_BADPROPVALUE"
    code = -106
    default_msg = "Invalid value for this property"


class DSOSHVisibleFlagError(DSAPIError):
    token = "DSJE_OSHVISIBLEFLAG"
    code = -107
    default_msg = (
        "Failed to set OSHVisible value"  # TODO: Is `set` right here?
    )


class DSBadEnvVarNameError(DSAPIError):
    token = "DSJE_BADENVVARNAME"
    code = -108
    default_msg = "Invalid environment variable name"


class DSBadEnvVarTypeError(DSAPIError):
    token = "DSJE_BADENVVARTYPE"
    code = -109
    default_msg = "Invalid environment variable type"


class DSBadEnvVarPromptError(DSAPIError):
    token = "DSJE_BADENVVARPROMPT"
    code = -110
    default_msg = "Missing environment variable prompt"


class DSReadEnvVarDefinitionsError(DSAPIError):
    token = "DSJE_READENVVARDEFNS"
    code = -111
    default_msg = "Failed to read environment variable definitions"


class DSReadEnvVarValuesError(DSAPIError):
    token = "DSJE_READENVVARVALUES"
    code = -112
    default_msg = "Failed to read environment variable values"


class DSWriteEnvVarDefinitionsError(DSAPIError):
    token = "DSJE_WRITEENVVARDEFNS"
    code = -113
    default_msg = "Failed to write environment variable definitions"


class DSWriteEnvVarValuesError(DSAPIError):
    token = "DSJE_WRITEENVVARVALUES"
    code = -114
    default_msg = "Failed to write environment variable values"


class DSDupEnvVarNameError(DSAPIError):
    token = "DSJE_DUPENVVARNAME"
    code = -115
    default_msg = "Environment variable name already exists"


class DSBadEnvVarError(DSAPIError):
    token = "DSJE_BADENVVAR"
    code = -116
    default_msg = "Environment variable does not exist"


class DSNotUserDefinedError(DSAPIError):
    token = "DSJE_NOTUSERDEFINED"
    code = -117
    default_msg = "Environment variable is not user-defined and therefore cannot be deleted"


class DSBadBooleanValueError(DSAPIError):
    token = "DSJE_BADBOOLEANVALUE"
    code = -118
    default_msg = "Invalid value given for a boolean environment variable"


class DSBadNumericValueError(DSAPIError):
    token = "DSJE_BADNUMERICVALUE"
    code = -119
    default_msg = "Invalid value given for a numeric environment variable"


class DSBadListValueError(DSAPIError):
    token = "DSJE_BADLISTVALUE"
    code = -120
    default_msg = "Invalid value given for a list environment variable"


class DSPXNotInstalledError(DSAPIError):
    token = "DSJE_PXNOTINSTALLED"
    code = -121
    default_msg = "Environment variable is specific to parallel jobs which are not available"


class DSIsParallelLicencedError(DSAPIError):
    token = "DSJE_ISPARALLELLICENCED"
    code = -122
    default_msg = "Failed to determine if parallel jobs are available"


class DSEncodeFailedError(DSAPIError):
    token = "DSJE_ENCODEFAILED"
    code = -123
    default_msg = "Failed to encode an encrypted value"


class DSDelProjectFailedError(DSAPIError):
    token = "DSJE_DELPROJFAILED"
    code = -124
    default_msg = "Failed to delete project definition"


class DSDelProjectFilesFailedError(DSAPIError):
    token = "DSJE_DELPROJFILESFAILED"
    code = -125
    default_msg = "Failed to delete project files"


class DSListScheduleFailedError(DSAPIError):
    token = "DSJE_LISTSCHEDULEFAILED"
    code = -126
    default_msg = "Failed to get list of scheduled jobs for project"


class DSClearScheduleFailedError(DSAPIError):
    token = "DSJE_CLEARSCHEDULEFAILED"
    code = -127
    default_msg = "Failed to clear scheduled jobs for project"


class DSBadProjectNameError(DSAPIError):
    token = "DSJE_BADPROJNAME"
    code = -128
    default_msg = "Project name contains invalid characters"


class DSGetDefaultPathFailedError(DSAPIError):
    token = "DSJE_GETDEFAULTPATHFAILED"
    code = -129
    default_msg = "Failed to determine default project directory"


class DSBadProjectLocationError(DSAPIError):
    token = "DSJE_BADPROJLOCATION"
    code = -130
    default_msg = "Project location path contains invalid characters"


class DSInvalidProjectLocationError(DSAPIError):
    token = "DSJE_INVALIDPROJECTLOCATION"
    code = -131
    default_msg = "Project location is invalid"


class DSOpenFailedError(DSAPIError):
    token = "DSJE_OPENFAILED"
    code = -132
    default_msg = "Failed to open file"


class DSReadUFailedError(DSAPIError):
    token = "DSJE_READUFAILED"
    code = -133
    default_msg = "Failed to lock administration record"


class DSAddProjectBlockedError(DSAPIError):
    token = "DSJE_ADDPROJECTBLOCKED"
    code = -134
    default_msg = "Administration record locked by another user"


class DSAddProjectFailedError(DSAPIError):
    token = "DSJE_ADDPROJECTFAILED"
    code = -135
    default_msg = "Failed to add project"


class DSLicenseProjectFailedError(DSAPIError):
    token = "DSJE_LICENSEPROJECTFAILED"
    code = -136
    default_msg = "Failed to license project"


class DSReleaseFailedError(DSAPIError):
    token = "DSJE_RELEASEFAILED"
    code = -137
    default_msg = "Failed to release administration record"


class DSDeleteProjectBlockedError(DSAPIError):
    token = "DSJE_DELETEPROJECTBLOCKED"
    code = -138
    default_msg = "Project locked by another user"


class DSNotAProjectError(DSAPIError):
    token = "DSJE_NOTAPROJECT"
    code = -139
    default_msg = "Failed to log to project"


class DSAccountPathFailedError(DSAPIError):
    token = "DSJE_ACCOUNTPATHFAILED"
    code = -140
    default_msg = "Failed to get account path"


class DSLogToFailedError(DSAPIError):
    token = "DSJE_LOGTOFAILED"
    code = -141
    default_msg = "Failed to log to UV account"


class DSProtectFailedError(DSAPIError):
    token = "DSJE_PROTECTFAILED"
    code = -142
    default_msg = "Protect or unprotect project failed"


class DSUnknownJobNameError(DSAPIError):
    token = "DSJE_UNKNOWN_JOBNAME"
    code = -201
    default_msg = "Could not find the supplied job name"


class DSNoMoreError(DSAPIError):
    token = "DSJE_NOMORE"
    code = -1001
    default_msg = "All events matching the filter criteria have been returned"


class DSBadProjectError(DSAPIError):
    token = "DSJE_BADPROJECT"
    code = -1002
    default_msg = "ProjectName is not a known project"


class DSNoDataStageError(DSAPIError):
    token = "DSJE_NO_DATASTAGE"
    code = -1003
    default_msg = "InfoSphere DataStage is not installed on system"


class DSOpenFailError(DSAPIError):
    token = "DSJE_OPENFAIL"
    code = -1004
    default_msg = "Failed to open job"


class DSNoMemoryError(DSAPIError):
    token = "DSJE_NO_MEMORY"
    code = -1005
    default_msg = "Failed to allocate dynamic memory"


class DSServerError(DSAPIError):
    token = "DSJE_SERVER_ERROR"
    code = -1006
    default_msg = "An unexpected or unknown error occurred in the engine"


class DSNotAvailableError(DSAPIError):
    token = "DSJE_NOT_AVAILABLE"
    code = -1007
    default_msg = "The requested information was not found"


class DSBadVersionError(DSAPIError):
    token = "DSJE_BAD_VERSION"
    code = -1008
    default_msg = "Version in DSOpenProjectEx is invalid"


class DSIncompatibleServerError(DSAPIError):
    token = "DSJE_INCOMPATIBLE_SERVER"
    code = -1009
    default_msg = "The engine version is incompatible with this version of the InfoSphere DataStage API"


class DSDomainLogToFailedError(DSAPIError):
    token = "DSJE_DOMAINLOGTOFAILED"
    code = -1010
    default_msg = "Failed to authenticate to Domain"


class DSNoPrivilegeError(DSAPIError):
    token = "DSJE_NOPRIVILEGE"
    code = -1011
    default_msg = "The isf user does not have sufficient DataStage privileges"


class DSLicenseExpiredError(DSAPIError):
    token = "DSJE_LICENSE_EXPIRED"
    code = 39121
    default_msg = "The InfoSphere DataStage license has expired"


class DSLimitReachedError(DSAPIError):
    token = "DSJE_LIMIT_REACHED"
    code = 39134
    default_msg = "The InfoSphere DataStage user limit has been reached"


class DSBadCredentialError(DSAPIError):
    token = "DSJE_BAD_CREDENTIAL"
    code = 80011
    default_msg = (
        "Incorrect system name or invalid user name or password provided"
    )


class DSPasswordExpiredError(DSAPIError):
    token = "DSJE_PASSWORD_EXPIRED"
    code = 80019
    default_msg = "Password has expired"


class DSBadHostError(DSAPIError):
    token = "DSJE_BAD_HOST"
    code = 81011
    default_msg = (
        "The host name specified is not valid, or the host is not responding"
    )


_CODE_TO_ERROR: dict[int, type[DSAPIError]] = {
    cls.code: cls for cls in DSAPIError.__subclasses__()
}


def raise_for_error(func: str, error_code: int, msg: str = "") -> NoReturn:
    """Raise the appropriate ``DSAPIError`` subclass for an error code."""
    exc_class = _CODE_TO_ERROR.get(error_code)
    if exc_class is not None:
        raise exc_class(func, msg)
    raise DSAPIError(func, msg, code=error_code)
