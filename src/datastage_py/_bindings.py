"""Python ctypes wrapper around the IBM DataStage API."""

from ctypes import (
    CDLL,
    POINTER,
    _Pointer,
    c_char,
    c_char_p,
    c_int,
    c_void_p,
    create_string_buffer,
    pointer,
)
from typing import TYPE_CHECKING, Literal, NoReturn

from datastage_py._constants import (
    CustInfoType,
    EnvVarType,
    JobInfoType,
    LimitType,
    LinkInfoType,
    LogEventType,
    ProjectInfoType,
    ReportType,
    ReposJobFilter,
    ReposObjectType,
    ReposRelationshipType,
    RunMode,
    StageInfoType,
    VarInfoType,
)
from datastage_py._structures import (
    DSCUSTINFO,
    DSJOB,
    DSJOBINFO,
    DSLINKINFO,
    DSLOGDETAIL,
    DSLOGDETAILFULL,
    DSLOGEVENT,
    DSPARAM,
    DSPARAMINFO,
    DSPROJECT,
    DSPROJECTINFO,
    DSREPORTINFO,
    DSREPOSINFO,
    DSREPOSJOBINFO,
    DSREPOSUSAGE,
    DSSTAGEINFO,
    DSVARINFO,
    time_t,
)
from datastage_py.exceptions import DSNoMoreError, raise_for_error
from datastage_py.utils import (
    decode_bytes,
    encode_string,
    parse_null_separated,
)

if TYPE_CHECKING:
    from pathlib import Path

type ProjectHandle = _Pointer[DSPROJECT]
type JobHandle = _Pointer[DSJOB]


class DSAPI:
    DSAPI_VERSION = 1

    def __init__(self) -> None:
        self.__api: CDLL | None = None
        self.__project_handle: ProjectHandle | None = None

    @property
    def _api(self) -> CDLL:
        if self.__api is None:
            msg = "Library not loaded; call DSLoadLibrary first"
            raise RuntimeError(msg)
        return self.__api

    def DSSetServerParams(
        self,
        domain_name: str,
        server_name: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._api.DSSetServerParams.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
        ]
        self._api.DSSetServerParams.restype = c_void_p

        self._api.DSSetServerParams(
            encode_string(domain_name),
            encode_string(username) if username is not None else None,
            encode_string(password) if password is not None else None,
            encode_string(server_name) if server_name is not None else None,
        )

    def DSGetProjectList(self) -> list[str]:
        self._api.DSGetProjectList.argtypes = []
        self._api.DSGetProjectList.restype = POINTER(c_char)

        project_list = self._api.DSGetProjectList()

        if project_list is None:
            self._raise_last_error("DSGetProjectList")
        return parse_null_separated(project_list)

    def DSOpenProject(self, name: str) -> ProjectHandle:
        self._api.DSOpenProjectEx.argtypes = [c_int, c_char_p]
        self._api.DSOpenProjectEx.restype = POINTER(DSPROJECT)

        handle: ProjectHandle = self._api.DSOpenProjectEx(
            self.DSAPI_VERSION, encode_string(name)
        )

        if handle is None:
            self._raise_last_error("DSOpenProject")

        self.__project_handle = handle
        return handle

    def DSGetProjectInfo(
        self, project_handle: ProjectHandle, info_type: ProjectInfoType
    ) -> DSPROJECTINFO:
        self._api.DSGetProjectInfo.argtypes = [
            POINTER(DSPROJECT),
            c_int,
            POINTER(DSPROJECTINFO),
        ]
        self._api.DSGetProjectInfo.restype = c_int

        proj_info = DSPROJECTINFO()
        res: int = self._api.DSGetProjectInfo(
            project_handle, info_type, pointer(proj_info)
        )

        if res != 0:
            self._raise_last_error("DSGetProjectInfo")
        return proj_info

    def DSGetLastError(self) -> tuple[int, str]:
        self._api.DSGetLastError.restype = c_int

        self._api.DSGetLastErrorMsg.argtypes = [POINTER(DSPROJECT)]
        self._api.DSGetLastErrorMsg.restype = c_char_p

        error_code = self._api.DSGetLastError()
        error_msg = ""

        # If `ProjectHandle` is NULL, `DSGetLastErrorMsg` retrieves the error
        # message associated with the last call to `DSOpenProject` or
        #  `DSGetProjectList`.
        if self.__project_handle is not None:
            error_msg = decode_bytes(
                self._api.DSGetLastErrorMsg(self.__project_handle)
            )
        return error_code, error_msg

    def DSOpenJob(self, project_handle: ProjectHandle, name: str) -> JobHandle:
        self._api.DSOpenJob.argtypes = [
            POINTER(DSPROJECT),
            c_char_p,
        ]
        self._api.DSOpenJob.restype = c_void_p

        handle: JobHandle | None = self._api.DSOpenJob(
            project_handle, c_char_p(encode_string(name))
        )

        if handle is None:
            self._raise_last_error("DSOpenJob")
        return handle

    def DSGetJobInfo(
        self, job_handle: JobHandle, info_type: JobInfoType
    ) -> DSJOBINFO:
        self._api.DSGetJobInfo.argtypes = [
            POINTER(DSJOB),
            c_int,
            POINTER(DSJOBINFO),
        ]
        self._api.DSGetJobInfo.restype = c_int

        job_info = DSJOBINFO()
        res: int = self._api.DSGetJobInfo(
            job_handle, info_type, pointer(job_info)
        )

        if res != 0:
            self._raise_last_error("DSGetJobInfo")
        return job_info

    def DSGetStageInfo(
        self, job_handle: JobHandle, name: str, info_type: StageInfoType
    ) -> DSSTAGEINFO:
        self._api.DSGetStageInfo.argtypes = [
            POINTER(DSJOB),
            c_char_p,
            c_int,
            POINTER(DSSTAGEINFO),
        ]
        self._api.DSGetStageInfo.restype = c_int

        stage_info = DSSTAGEINFO()
        res: int = self._api.DSGetStageInfo(
            job_handle,
            encode_string(name),
            info_type,
            pointer(stage_info),
        )

        if res != 0:
            self._raise_last_error("DSGetStageInfo")
        return stage_info

    def DSGetLinkInfo(
        self,
        job_handle: JobHandle,
        stage_name: str,
        name: str,
        info_type: LinkInfoType,
    ) -> DSLINKINFO:
        self._api.DSGetLinkInfo.argtypes = [
            POINTER(DSJOB),
            c_char_p,
            c_char_p,
            c_int,
            POINTER(DSLINKINFO),
        ]
        self._api.DSGetLinkInfo.restype = c_int

        link_info = DSLINKINFO()
        res: int = self._api.DSGetLinkInfo(
            job_handle,
            encode_string(stage_name),
            encode_string(name),
            info_type,
            pointer(link_info),
        )

        if res != 0:
            self._raise_last_error("DSGetLinkInfo")
        return link_info

    def DSGetVarInfo(
        self,
        job_handle: JobHandle,
        stage_name: str,
        name: str,
        info_type: VarInfoType,
    ) -> DSVARINFO:
        self._api.DSGetVarInfo.argtypes = [
            POINTER(DSJOB),
            c_char_p,
            c_char_p,
            c_int,
            POINTER(DSVARINFO),
        ]
        self._api.DSGetVarInfo.restype = c_int

        var_info = DSVARINFO()
        res: int = self._api.DSGetVarInfo(
            job_handle,
            encode_string(stage_name),
            encode_string(name),
            info_type,
            pointer(var_info),
        )

        if res != 0:
            self._raise_last_error("DSGetVarInfo")
        return var_info

    def DSGetCustInfo(
        self,
        job_handle: JobHandle,
        stage_name: str,
        name: str,
        info_type: CustInfoType,
    ) -> DSCUSTINFO:
        self._api.DSGetCustInfo.argtypes = [
            POINTER(DSJOB),
            c_char_p,
            c_char_p,
            c_int,
            POINTER(DSCUSTINFO),
        ]
        self._api.DSGetCustInfo.restype = c_int

        cust_info = DSCUSTINFO()
        res: int = self._api.DSGetCustInfo(
            job_handle,
            encode_string(stage_name),
            encode_string(name),
            info_type,
            pointer(cust_info),
        )

        if res != 0:
            self._raise_last_error("DSGetCustInfo")
        return cust_info

    def DSFindFirstLogEntry(
        self,
        job_handle: JobHandle,
        event_type: LogEventType = LogEventType.ANY,
        start_time: int = 0,
        end_time: int = 0,
        max_number: int = 500,
    ) -> DSLOGEVENT | None:
        """Retrieve all the log entries that meet a specified criteria.

        Args:
            job_handle: The job handle.
            event_type: The type of event.
            start_time: Limits the returned log events to those that occurred
                on or after the specified date and time. Set this value to 0
                to return the earliest event.
            end_time: Limits the returned log events to those that occurred
                before the specified date and time. Set this value to 0 to
                return all entries up to the most recent.
            max_number: Specifies the maximum number of log entries to
                retrieve, starting from the latest.
        """
        self._api.DSFindFirstLogEntry.argtypes = [
            POINTER(DSJOB),
            c_int,
            time_t,
            time_t,
            c_int,
            POINTER(DSLOGEVENT),
        ]
        self._api.DSFindFirstLogEntry.restype = c_int

        log_info = DSLOGEVENT()
        res: int = self._api.DSFindFirstLogEntry(
            job_handle,
            event_type,
            start_time,
            end_time,
            max_number,
            pointer(log_info),
        )

        if res != 0:
            if res == DSNoMoreError.code:
                return None
            self._raise_last_error("DSFindFirstLogEntry")
        return log_info

    def DSFindNextLogEntry(self, job_handle: JobHandle) -> DSLOGEVENT | None:
        self._api.DSFindNextLogEntry.argtypes = [
            POINTER(DSJOB),
            POINTER(DSLOGEVENT),
        ]
        self._api.DSFindNextLogEntry.restype = c_int

        log_event = DSLOGEVENT()
        res: int = self._api.DSFindNextLogEntry(job_handle, pointer(log_event))

        if res != 0:
            if res == DSNoMoreError.code:
                return None
            self._raise_last_error("DSFindNextLogEntry")
        return log_event

    def DSGetLogEntryFull(
        self, job_handle: JobHandle, event_id: int
    ) -> DSLOGDETAILFULL:
        self._api.DSGetLogEntryFull.argtypes = [
            POINTER(DSJOB),
            c_int,
            POINTER(DSLOGDETAILFULL),
        ]
        self._api.DSGetLogEntryFull.restype = c_int

        log_detail = DSLOGDETAILFULL()
        res: int = self._api.DSGetLogEntryFull(
            job_handle, event_id, pointer(log_detail)
        )

        if res != 0:
            self._raise_last_error("DSGetLogEntryFull")
        return log_detail

    def DSGetLogEntry(
        self, job_handle: JobHandle, event_id: int
    ) -> DSLOGDETAIL:
        self._api.DSGetLogEntry.argtypes = [
            POINTER(DSJOB),
            c_int,
            POINTER(DSLOGDETAIL),
        ]
        self._api.DSGetLogEntry.restype = c_int

        log_detail = DSLOGDETAIL()
        res: int = self._api.DSGetLogEntry(
            job_handle, event_id, pointer(log_detail)
        )

        if res != 0:
            self._raise_last_error("DSGetLogEntry")
        return log_detail

    def DSGetNewestLogId(
        self, job_handle: JobHandle, event_type: LogEventType
    ) -> int:
        self._api.DSGetNewestLogId.argtypes = [POINTER(DSJOB), c_int]
        self._api.DSGetNewestLogId.restype = c_int

        last_log_id: int = self._api.DSGetNewestLogId(job_handle, event_type)

        if last_log_id == -1:
            self._raise_last_error("DSGetNewestLogId")
        return last_log_id

    def DSGetLogEventIds(
        self, job_handle: JobHandle, run_number: int = 0, filter_type: str = ""
    ) -> list[str]:
        self._api.DSGetLogEventIds.argtypes = [
            POINTER(DSJOB),
            c_int,
            c_char_p,
            POINTER(POINTER(c_char)),
        ]
        self._api.DSGetLogEventIds.restype = c_int

        events_pointer = POINTER(c_char)()
        res: int = self._api.DSGetLogEventIds(
            job_handle,
            run_number,
            encode_string(filter_type),
            pointer(events_pointer),
        )

        if res != 0:
            self._raise_last_error("DSGetLogEventIds")
        return parse_null_separated(events_pointer)

    def DSGetQueueList(self) -> list[str]:
        self._api.DSGetQueueList.restype = POINTER(c_char)
        q_list = self._api.DSGetQueueList()

        return parse_null_separated(q_list)

    def DSSetJobQueue(self, job_handle: JobHandle, name: str) -> None:
        self._api.DSSetJobQueue.argtypes = [POINTER(DSJOB), c_char_p]
        self._api.DSSetJobQueue.restype = c_int

        res: int = self._api.DSSetJobQueue(job_handle, encode_string(name))

        if res != 0:
            self._raise_last_error("DSSetJobQueue")

    def DSCloseJob(self, job_handle: JobHandle) -> None:
        self._api.DSCloseJob.argtypes = [POINTER(DSJOB)]
        self._api.DSCloseJob.restype = c_int

        res: int = self._api.DSCloseJob(job_handle)

        if res != 0:
            self._raise_last_error("DSCloseJob")

    def DSCloseProject(self, project_handle: ProjectHandle) -> None:
        self._api.DSCloseProject.argtypes = [POINTER(DSPROJECT)]
        self._api.DSCloseProject.restype = c_int

        res: int = self._api.DSCloseProject(project_handle)

        if res != 0:
            self._raise_last_error("DSCloseProject")
        self.__project_handle = None

    def DSSetJobLimit(
        self, job_handle: JobHandle, limit_type: LimitType, value: int
    ) -> None:
        self._api.DSSetJobLimit.argtypes = [POINTER(DSJOB), c_int, c_int]
        self._api.DSSetJobLimit.restype = c_int

        res: int = self._api.DSSetJobLimit(job_handle, limit_type, value)

        if res != 0:
            self._raise_last_error("DSSetJobLimit")

    def DSPurgeJob(self, job_handle: JobHandle, purge_spec: int) -> None:
        self._api.DSPurgeJob.argtypes = [POINTER(DSJOB), c_int]
        self._api.DSPurgeJob.restype = c_int

        res: int = self._api.DSPurgeJob(job_handle, purge_spec)

        if res != 0:
            self._raise_last_error("DSPurgeJob")

    def DSRunJob(self, job_handle: JobHandle, run_mode: RunMode) -> None:
        self._api.DSRunJob.argtypes = [POINTER(DSJOB), c_int]
        self._api.DSRunJob.restype = c_int

        res: int = self._api.DSRunJob(job_handle, run_mode)

        if res != 0:
            self._raise_last_error("DSRunJob")

    def DSStopJob(self, job_handle: JobHandle) -> None:
        self._api.DSStopJob.argtypes = [POINTER(DSJOB)]
        self._api.DSStopJob.restype = c_int

        res: int = self._api.DSStopJob(job_handle)

        if res != 0:
            self._raise_last_error("DSStopJob")

    def DSLockJob(self, job_handle: JobHandle) -> None:
        self._api.DSLockJob.argtypes = [POINTER(DSJOB)]
        self._api.DSLockJob.restype = c_int

        res: int = self._api.DSLockJob(job_handle)

        if res != 0:
            self._raise_last_error("DSLockJob")

    def DSUnlockJob(self, job_handle: JobHandle) -> None:
        self._api.DSUnlockJob.argtypes = [POINTER(DSJOB)]
        self._api.DSUnlockJob.restype = c_int

        res: int = self._api.DSUnlockJob(job_handle)

        if res != 0:
            self._raise_last_error("DSUnlockJob")

    def DSWaitForJob(self, job_handle: JobHandle) -> None:
        self._api.DSWaitForJob.argtypes = [POINTER(DSJOB)]
        self._api.DSWaitForJob.restype = c_int

        res: int = self._api.DSWaitForJob(job_handle)

        if res != 0:
            self._raise_last_error("DSWaitForJob")

    def DSSetParam(
        self, job_handle: JobHandle, name: str, param: DSPARAM
    ) -> None:
        self._api.DSSetParam.argtypes = [
            POINTER(DSJOB),
            c_char_p,
            POINTER(DSPARAM),
        ]
        self._api.DSSetParam.restype = c_int

        res: int = self._api.DSSetParam(
            job_handle, encode_string(name), pointer(param)
        )

        if res != 0:
            self._raise_last_error("DSSetParam")

    def DSGetParamInfo(self, job_handle: JobHandle, name: str) -> DSPARAMINFO:
        self._api.DSGetParamInfo.argtypes = [
            POINTER(DSJOB),
            c_char_p,
            POINTER(DSPARAMINFO),
        ]
        self._api.DSGetParamInfo.restype = c_int

        param_info = DSPARAMINFO()
        res: int = self._api.DSGetParamInfo(
            job_handle, encode_string(name), pointer(param_info)
        )

        if res != 0:
            self._raise_last_error("DSGetParamInfo")
        return param_info

    def DSMakeJobReport(
        self,
        job_handle: JobHandle,
        report_type: ReportType,
        line_sep: Literal["CRLF", "LF", "CR"],
    ):  # TODO: Add type hint
        """Generate a job report.

        Args:
            job_handle: Job handle.
            report_type: Report type.
            line_sep: Line separator in the report. Defaults to CRLF on
                Windows and LF on other platforms.
        """
        self._api.DSMakeJobReport.argtypes = [
            POINTER(DSJOB),
            c_int,
            c_char_p,
            POINTER(DSREPORTINFO),
        ]
        self._api.DSMakeJobReport.restype = c_int

        report_info = DSREPORTINFO()
        res: int = self._api.DSMakeJobReport(
            job_handle,
            report_type,
            encode_string(line_sep),
            pointer(report_info),
        )

        if res != 0:
            self._raise_last_error("DSMakeJobReport")
        return report_info.info.reportText

    def DSGetReposUsage(
        self,
        project_handle: ProjectHandle,
        relationship_type: ReposRelationshipType,
        object_name: str,
        *,
        recursive: bool = False,
    ) -> None | DSREPOSUSAGE:
        self._api.DSGetReposUsage.argtypes = [
            POINTER(DSPROJECT),
            c_int,
            c_char_p,
            c_int,
            POINTER(DSREPOSUSAGE),
        ]
        self._api.DSGetReposUsage.restype = c_int

        repos_usage = DSREPOSUSAGE()

        # On success, `DSGetReposUsage` returns the number of objects that have
        # been found.
        res: int = self._api.DSGetReposUsage(
            project_handle,
            relationship_type,
            encode_string(object_name),
            int(recursive),
            pointer(repos_usage),
        )

        if res < 0:
            self._raise_last_error("DSGetReposUsage")
        if res == 0:
            return None

        return repos_usage.info.jobs.contents

    def DSGetReposInfo(  # noqa: PLR0913
        self,
        project_handle: ProjectHandle,
        object_type: ReposObjectType,
        info_type: ReposJobFilter,
        search_criteria: str,
        starting_category: str,
        *,
        subcategories: bool = False,
    ) -> None | DSREPOSJOBINFO:
        self._api.DSGetReposInfo.argtypes = [
            POINTER(DSPROJECT),
            c_int,
            c_int,
            c_char_p,
            c_char_p,
            c_int,
            POINTER(DSREPOSINFO),
        ]
        self._api.DSGetReposInfo.restype = c_int

        repos_info = DSREPOSINFO()

        # On success, `DSGetReposInfo` returns the number of objects that have
        # been found.
        res: int = self._api.DSGetReposInfo(
            project_handle,
            object_type,
            info_type,
            encode_string(search_criteria),
            encode_string(starting_category),
            int(subcategories),
            pointer(repos_info),
        )

        if res < 0:
            self._raise_last_error("DSGetReposInfo")
        if res == 0:
            return None

        return repos_info.info.jobs.contents

    def DSLogEvent(
        self, job_handle: JobHandle, event_type: LogEventType, message: str
    ) -> None:
        self._api.DSLogEvent.argtypes = [
            POINTER(DSJOB),
            c_int,
            c_char_p,
            c_char_p,
        ]
        self._api.DSLogEvent.restype = c_int

        res: int = self._api.DSLogEvent(
            job_handle, event_type, None, encode_string(message)
        )

        if res != 0:
            self._raise_last_error("DSLogEvent")

    def DSAddEnvVar(
        self,
        project_handle: ProjectHandle,
        name: str,
        var_type: EnvVarType,
        prompt_text: str,
        value: str,
    ) -> None:
        self._api.DSAddEnvVar.argtypes = [
            POINTER(DSPROJECT),
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
        ]
        self._api.DSAddEnvVar.restype = c_int

        res: int = self._api.DSAddEnvVar(
            project_handle,
            encode_string(name),
            encode_string(var_type),
            encode_string(prompt_text),
            encode_string(value),
        )

        if res != 0:
            self._raise_last_error("DSAddEnvVar")

    def DSDeleteEnvVar(self, project_handle: ProjectHandle, name: str) -> None:
        self._api.DSDeleteEnvVar.argtypes = [POINTER(DSPROJECT), c_char_p]
        self._api.DSDeleteEnvVar.restype = c_int

        res: int = self._api.DSDeleteEnvVar(
            project_handle, encode_string(name)
        )

        if res != 0:
            self._raise_last_error("DSDeleteEnvVar")

    def DSSetEnvVar(
        self, project_handle: ProjectHandle, name: str, value: str
    ) -> None:
        self._api.DSSetEnvVar.argtypes = [
            POINTER(DSPROJECT),
            c_char_p,
            c_char_p,
        ]
        self._api.DSSetEnvVar.restype = c_int

        res: int = self._api.DSSetEnvVar(
            project_handle, encode_string(name), encode_string(value)
        )

        if res != 0:
            self._raise_last_error("DSSetEnvVar")

    def DSListEnvVars(self, project_handle: ProjectHandle) -> list[str]:
        self._api.DSListEnvVars.argtypes = [POINTER(DSPROJECT)]
        self._api.DSListEnvVars.restype = POINTER(c_char)

        res = self._api.DSListEnvVars(project_handle)

        if not res:
            self._raise_last_error("DSListEnvVars")
        return parse_null_separated(res)

    def DSAddProject(self, name: str, location: str = "") -> None:
        self._api.DSAddProject.argtypes = [c_char_p, c_char_p]
        self._api.DSAddProject.restype = c_int

        res: int = self._api.DSAddProject(
            encode_string(name), encode_string(location)
        )

        if res != 0:
            self._raise_last_error("DSAddProject")

    def DSDeleteProject(self, name: str) -> None:
        self._api.DSDeleteProject.argtypes = [c_char_p]
        self._api.DSDeleteProject.restype = c_int

        res: int = self._api.DSDeleteProject(encode_string(name))

        if res != 0:
            self._raise_last_error("DSDeleteProject")

    def DSGetIdForJob(
        self, project_handle: ProjectHandle, name: str
    ) -> c_char_p:
        self._api.DSGetIdForJob.argtypes = [POINTER(DSPROJECT), c_char_p]
        self._api.DSGetIdForJob.restype = c_char_p

        res = self._api.DSGetIdForJob(project_handle, encode_string(name))

        if not res:
            self._raise_last_error("DSGetIdForJob")
        return res

    def DSSetIdForJob(
        self, project_handle: ProjectHandle, name: str, job_id: str
    ) -> None:
        self._api.DSSetIdForJob.argtypes = [
            POINTER(DSPROJECT),
            c_char_p,
            c_char_p,
        ]
        self._api.DSSetIdForJob.restype = c_int

        res: int = self._api.DSSetIdForJob(
            project_handle, encode_string(name), encode_string(job_id)
        )

        if res != 0:
            self._raise_last_error("DSSetIdForJob")

    def DSJobNameFromJobId(
        self, project_handle: ProjectHandle, job_id: str
    ) -> c_char_p:
        self._api.DSJobNameFromJobId.argtypes = [POINTER(DSPROJECT), c_char_p]
        self._api.DSJobNameFromJobId.restype = c_char_p

        res = self._api.DSJobNameFromJobId(
            project_handle, encode_string(job_id)
        )

        if not res:
            self._raise_last_error("DSJobNameFromJobId")
        return res

    def DSServerMessage(
        self,
        message: str,
        params: list | None = None,
        message_id: str = "",
        message_size: int = 1000,
    ):
        if params is None:
            params = []

        if not isinstance(params, list):
            msg = "Parameters must be a list"
            raise TypeError(msg)

        max_params = len(params)

        self._api.DSServerMessage.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p * max_params,
            c_char_p,
            c_int,
        ]
        self._api.DSServerMessage.restype = c_int

        encoded_params = [encode_string(str(prm)) for prm in params]
        res_message = create_string_buffer(
            message_size
        )  # TODO: Can `message_size` be calculated at runtime?

        # TODO: `msg_size` not in use?
        msg_size: int = self._api.DSServerMessage(
            encode_string(message_id),
            encode_string(message),
            (c_char_p * max_params)(*encoded_params),
            res_message,
            message_size,
        )

        if not res_message:
            self._raise_last_error("DSServerMessage")
        return res_message.value

    def DSSetProjectProperty(
        self, project_handle: ProjectHandle, name: str, value: str
    ) -> None:
        self._api.DSSetProjectProperty.argtypes = [
            POINTER(DSPROJECT),
            c_char_p,
            c_char_p,
        ]
        self._api.DSSetProjectProperty.restype = c_int

        res: int = self._api.DSSetProjectProperty(
            project_handle, encode_string(name), encode_string(value)
        )

        if res != 0:
            self._raise_last_error("DSSetProjectProperty")

    def DSListProjectProperties(
        self, project_handle: ProjectHandle
    ) -> list[str]:
        self._api.DSListProjectProperties.argtypes = [POINTER(DSPROJECT)]
        self._api.DSListProjectProperties.restype = POINTER(c_char)

        res = self._api.DSListProjectProperties(project_handle)

        if not res:
            self._raise_last_error("DSListProjectProperties")
        return parse_null_separated(res)

    def DSGetWLMEnabled(self) -> None:
        self._api.DSGetWLMEnabled.argtypes = []
        self._api.DSGetWLMEnabled.restype = c_int

        res: int = self._api.DSGetWLMEnabled()

        if not res:
            self._raise_last_error("DSGetWLMEnabled")

    def DSSetGenerateOpMetaData(
        self, job_handle: JobHandle, value: int
    ) -> None:
        self._api.DSSetGenerateOpMetaData.argtypes = [POINTER(DSJOB), c_int]
        self._api.DSSetGenerateOpMetaData.restype = c_int

        res: int = self._api.DSSetGenerateOpMetaData(job_handle, value)

        if res != 0:
            self._raise_last_error("DSSetGenerateOpMetaData")

    def DSSetDisableProjectHandler(
        self, project_handle: ProjectHandle, value: int
    ) -> None:
        self._api.DSSetDisableProjectHandler.argtypes = [
            POINTER(DSPROJECT),
            c_int,
        ]
        self._api.DSSetDisableProjectHandler.restype = c_int

        res: int = self._api.DSSetDisableProjectHandler(project_handle, value)

        if res != 0:
            self._raise_last_error("DSSetDisableProjectHandler")

    def DSSetDisableJobHandler(
        self, job_handle: JobHandle, value: int
    ) -> None:
        self._api.DSSetDisableJobHandler.argtypes = [POINTER(DSJOB), c_int]
        self._api.DSSetDisableJobHandler.restype = c_int

        res: int = self._api.DSSetDisableJobHandler(job_handle, value)

        if res != 0:
            self._raise_last_error("DSSetDisableJobHandler")

    def DSLoadLibrary(self, file: Path) -> None:
        """Load the shared library.

        Args:
            file: Path to library file.

        The DataStage API has a runtime dependency on the `vmdsapi.dll` library
        on Windows and `libvmdsapi.so` library on Unix.
        """
        if not file.is_file():
            msg = f"Library not found: {file!r}"
            raise FileNotFoundError(msg)

        try:
            self.__api = CDLL(file)
        except OSError as exc:
            msg = "Cannot load the library"
            raise OSError(msg) from exc

    def DSUnloadLibrary(self) -> None:
        self.__api = None
        self.__project_handle = None

    def _raise_last_error(self, func: str) -> NoReturn:
        code, msg = self.DSGetLastError()
        raise_for_error(func, code, msg)
