"""Python ctypes wrapper around the IBM DataStage API."""

from ctypes import (
    CDLL,
    POINTER,
    c_char,
    c_char_p,
    c_int,
    c_void_p,
    pointer,
)
from typing import TYPE_CHECKING, Literal, NoReturn

from datastage_py.enums import (
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
from datastage_py.exceptions import DSNoMoreError, raise_for_error
from datastage_py.structures import (
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
    DSREPOSUSAGE,
    DSSTAGEINFO,
    DSVARINFO,
    time_t,
)
from datastage_py.utils import (
    decode_bytes,
    encode_string,
    split_char_p,
)

if TYPE_CHECKING:
    from ctypes import _Pointer
    from pathlib import Path

    ProjectHandle = _Pointer[DSPROJECT]
    JobHandle = _Pointer[DSJOB]
else:
    ProjectHandle = POINTER(DSPROJECT)
    JobHandle = POINTER(DSJOB)


class DSAPI:
    DSAPI_VERSION = 1

    def __init__(self) -> None:
        """Initialise the `DSAPI` instance."""
        self.__api: CDLL | None = None
        self.__project_name = None

    @property
    def _api(self) -> CDLL:
        if self.__api is None:
            msg = "Library not loaded; call DSLoadLibrary first"
            raise RuntimeError(msg)
        return self.__api

    def _raise_last_error(self, func: str) -> NoReturn:
        code, msg = self.DSGetLastError()
        raise_for_error(func, code, msg)

    def DSSetServerParams(
        self, domain_name: str, server_name: str, username: str, password: str
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
            encode_string(username),
            encode_string(password),
            encode_string(server_name),
        )

    def DSGetProjectList(self) -> list[str]:
        self._api.DSGetProjectList.argtypes = []
        self._api.DSGetProjectList.restype = POINTER(c_char)

        project_list = self._api.DSGetProjectList()

        if not project_list:
            self._raise_last_error("DSGetProjectList")
        return split_char_p(project_list)

    def DSOpenProject(self, project_name: str) -> ProjectHandle:
        self._api.DSOpenProjectEx.argtypes = [c_int, c_char_p]
        self._api.DSOpenProjectEx.restype = POINTER(DSPROJECT)

        handle = self._api.DSOpenProjectEx(
            self.DSAPI_VERSION, encode_string(project_name)
        )

        if not handle:
            self._raise_last_error("DSOpenProject")
        self.__project_name = handle
        return handle

    def DSGetProjectInfo(
        self, project_name: ProjectHandle, info_type: ProjectInfoType
    ) -> DSPROJECTINFO:
        self._api.DSGetProjectInfo.argtypes = [
            POINTER(DSPROJECT),
            c_int,
            POINTER(DSPROJECTINFO),
        ]
        self._api.DSGetProjectInfo.restype = c_int

        proj_info = DSPROJECTINFO()
        res = self._api.DSGetProjectInfo(
            project_name, info_type, pointer(proj_info)
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

        if self.__project_name is not None:
            error_msg = decode_bytes(
                self._api.DSGetLastErrorMsg(self.__project_name)
            )

        return error_code, error_msg

    def DSOpenJob(
        self, project_name: ProjectHandle, job_name: str
    ) -> JobHandle:
        self._api.DSOpenJob.argtypes = [
            POINTER(DSPROJECT),
            c_char_p,
        ]
        self._api.DSOpenJob.restype = POINTER(DSJOB)

        handle = self._api.DSOpenJob(
            project_name, c_char_p(encode_string(job_name))
        )

        if not handle:
            self._raise_last_error("DSOpenJob")
        return handle

    def DSGetJobInfo(
        self, job_name: JobHandle, info_type: JobInfoType
    ) -> DSJOBINFO:
        self._api.DSGetJobInfo.argtypes = [
            POINTER(DSJOB),
            c_int,
            POINTER(DSJOBINFO),
        ]
        self._api.DSGetJobInfo.restype = c_int

        job_info = DSJOBINFO()
        res = self._api.DSGetJobInfo(job_name, info_type, pointer(job_info))

        if res != 0:
            self._raise_last_error("DSGetJobInfo")
        return job_info

    def DSGetStageInfo(
        self, job_name: JobHandle, stage_name: str, info_type: StageInfoType
    ) -> DSSTAGEINFO:
        self._api.DSGetStageInfo.argtypes = [
            POINTER(DSJOB),
            c_char_p,
            c_int,
            POINTER(DSSTAGEINFO),
        ]
        self._api.DSGetStageInfo.restype = c_int

        stage_info = DSSTAGEINFO()
        res = self._api.DSGetStageInfo(
            job_name,
            encode_string(stage_name),
            info_type,
            pointer(stage_info),
        )

        if res != 0:
            self._raise_last_error("DSGetStageInfo")
        return stage_info

    def DSGetLinkInfo(
        self,
        job_name: JobHandle,
        stage_name: str,
        link_name: str,
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
        res = self._api.DSGetLinkInfo(
            job_name,
            encode_string(stage_name),
            encode_string(link_name),
            info_type,
            pointer(link_info),
        )

        if res != 0:
            self._raise_last_error("DSGetLinkInfo")
        return link_info

    def DSGetVarInfo(
        self,
        job_name: JobHandle,
        stage_name: str,
        var_name: str,
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
        res = self._api.DSGetVarInfo(
            job_name,
            encode_string(stage_name),
            encode_string(var_name),
            info_type,
            pointer(var_info),
        )

        if res != 0:
            self._raise_last_error("DSGetVarInfo")
        return var_info

    def DSGetCustInfo(
        self,
        job_name: JobHandle,
        stage_name: str,
        cust_info_name: str,
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
        res = self._api.DSGetCustInfo(
            job_name,
            encode_string(stage_name),
            encode_string(cust_info_name),
            info_type,
            pointer(cust_info),
        )

        if res != 0:
            self._raise_last_error("DSGetCustInfo")
        return cust_info

    def DSFindFirstLogEntry(
        self,
        job_name: JobHandle,
        event_type: LogEventType = LogEventType.ANY,
        start_time: int = 0,
        end_time: int = 0,
        max_number: int = 500,
    ) -> DSLOGEVENT | None:
        """Retrieve all the log entries that meet a specified criteria.

        Args:
            job_name: The name of the job.
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
        res = self._api.DSFindFirstLogEntry(
            job_name,
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

    def DSFindNextLogEntry(self, job_name: JobHandle) -> DSLOGEVENT | None:
        self._api.DSFindNextLogEntry.argtypes = [
            POINTER(DSJOB),
            POINTER(DSLOGEVENT),
        ]
        self._api.DSFindNextLogEntry.restype = c_int

        log_event = DSLOGEVENT()
        res = self._api.DSFindNextLogEntry(job_name, pointer(log_event))

        if res != 0:
            if res == DSNoMoreError.code:
                return None
            self._raise_last_error("DSFindNextLogEntry")
        return log_event

    def DSGetLogEntryFull(
        self, job_name: JobHandle, event_id: int
    ) -> DSLOGDETAILFULL:
        self._api.DSGetLogEntryFull.argtypes = [
            POINTER(DSJOB),
            c_int,
            POINTER(DSLOGDETAILFULL),
        ]
        self._api.DSGetLogEntryFull.restype = c_int

        log_detail = DSLOGDETAILFULL()
        res = self._api.DSGetLogEntryFull(
            job_name, event_id, pointer(log_detail)
        )

        if res != 0:
            self._raise_last_error("DSGetLogEntryFull")
        return log_detail

    def DSGetLogEntry(self, job_name: JobHandle, event_id: int) -> DSLOGDETAIL:
        self._api.DSGetLogEntry.argtypes = [
            POINTER(DSJOB),
            c_int,
            POINTER(DSLOGDETAIL),
        ]
        self._api.DSGetLogEntry.restype = c_int

        log_detail = DSLOGDETAIL()
        res = self._api.DSGetLogEntry(job_name, event_id, pointer(log_detail))

        if res != 0:
            self._raise_last_error("DSGetLogEntry")
        return log_detail

    def DSGetNewestLogId(
        self, job_name: JobHandle, event_type: LogEventType
    ) -> int:
        self._api.DSGetNewestLogId.argtypes = [POINTER(DSJOB), c_int]
        self._api.DSGetNewestLogId.restype = c_int

        last_log_id = self._api.DSGetNewestLogId(job_name, event_type)

        if last_log_id == -1:
            self._raise_last_error("DSGetNewestLogId")
        return last_log_id

    def DSGetLogEventIds(
        self, job_name: JobHandle, run_number: int = 0, filter_type: str = ""
    ) -> list[str]:
        self._api.DSGetLogEventIds.argtypes = [
            POINTER(DSJOB),
            c_int,
            c_char_p,
            POINTER(POINTER(c_char)),
        ]
        self._api.DSGetLogEventIds.restype = c_int

        events_pointer = POINTER(c_char)()
        res = self._api.DSGetLogEventIds(
            job_name,
            run_number,
            encode_string(filter_type),
            pointer(events_pointer),
        )

        if res != 0:
            self._raise_last_error("DSGetLogEventIds")
        return split_char_p(events_pointer)

    def DSGetQueueList(self) -> list[str]:
        self._api.DSGetQueueList.restype = POINTER(c_char)
        q_list = self._api.DSGetQueueList()

        return split_char_p(q_list)

    def DSSetJobQueue(self, job_name: JobHandle, queue_name: str) -> None:
        self._api.DSSetJobQueue.argtypes = [POINTER(DSJOB), c_char_p]
        self._api.DSSetJobQueue.restype = c_int

        res = self._api.DSSetJobQueue(job_name, encode_string(queue_name))

        if res != 0:
            self._raise_last_error("DSSetJobQueue")

    def DSCloseJob(self, job_name: JobHandle) -> None:
        self._api.DSCloseJob.argtypes = [POINTER(DSJOB)]
        self._api.DSCloseJob.restype = c_int

        res = self._api.DSCloseJob(job_name)

        if res != 0:
            self._raise_last_error("DSCloseJob")

    def DSCloseProject(self, project_name: ProjectHandle) -> None:
        self._api.DSCloseProject.argtypes = [POINTER(DSPROJECT)]
        self._api.DSCloseProject.restype = c_int

        res = self._api.DSCloseProject(project_name)

        if res != 0:
            self._raise_last_error("DSCloseProject")
        self.__project_name = None

    def DSSetJobLimit(
        self, job_name: JobHandle, limit_type: LimitType, limit_value: int
    ) -> None:
        self._api.DSSetJobLimit.argtypes = [POINTER(DSJOB), c_int, c_int]
        self._api.DSSetJobLimit.restype = c_int

        res = self._api.DSSetJobLimit(job_name, limit_type, limit_value)

        if res != 0:
            self._raise_last_error("DSSetJobLimit")

    def DSPurgeJob(self, job_name: JobHandle, purge_spec: int) -> None:
        self._api.DSPurgeJob.argtypes = [POINTER(DSJOB), c_int]
        self._api.DSPurgeJob.restype = c_int

        res = self._api.DSPurgeJob(job_name, purge_spec)

        if res != 0:
            self._raise_last_error("DSPurgeJob")

    def DSRunJob(self, job_name: JobHandle, run_mode: RunMode) -> None:
        self._api.DSRunJob.argtypes = [POINTER(DSJOB), c_int]
        self._api.DSRunJob.restype = c_int

        res = self._api.DSRunJob(job_name, run_mode)

        if res != 0:
            self._raise_last_error("DSRunJob")

    def DSStopJob(self, job_name: JobHandle) -> None:
        self._api.DSStopJob.argtypes = [POINTER(DSJOB)]
        self._api.DSStopJob.restype = c_int

        res = self._api.DSStopJob(job_name)

        if res != 0:
            self._raise_last_error("DSStopJob")

    def DSLockJob(self, job_name: JobHandle) -> None:
        self._api.DSLockJob.argtypes = [POINTER(DSJOB)]
        self._api.DSLockJob.restype = c_int

        res = self._api.DSLockJob(job_name)

        if res != 0:
            self._raise_last_error("DSLockJob")

    def DSUnlockJob(self, job_name: JobHandle) -> None:
        self._api.DSUnlockJob.argtypes = [POINTER(DSJOB)]
        self._api.DSUnlockJob.restype = c_int

        res = self._api.DSUnlockJob(job_name)

        if res != 0:
            self._raise_last_error("DSUnlockJob")

    def DSWaitForJob(self, job_name: JobHandle) -> None:
        self._api.DSWaitForJob.argtypes = [POINTER(DSJOB)]
        self._api.DSWaitForJob.restype = c_int

        res = self._api.DSWaitForJob(job_name)

        if res != 0:
            self._raise_last_error("DSWaitForJob")

    def DSSetParam(
        self, job_name: JobHandle, param_name: str, param: DSPARAM
    ) -> None:
        self._api.DSSetParam.argtypes = [
            POINTER(DSJOB),
            c_char_p,
            POINTER(DSPARAM),
        ]
        self._api.DSSetParam.restype = c_int

        res = self._api.DSSetParam(
            job_name, encode_string(param_name), pointer(param)
        )

        if res != 0:
            self._raise_last_error("DSSetParam")

    def DSGetParamInfo(
        self, job_name: JobHandle, param_name: str
    ) -> DSPARAMINFO:
        self._api.DSGetParamInfo.argtypes = [
            POINTER(DSJOB),
            c_char_p,
            POINTER(DSPARAMINFO),
        ]
        self._api.DSGetParamInfo.restype = c_int

        param_info = DSPARAMINFO()
        res = self._api.DSGetParamInfo(
            job_name, encode_string(param_name), pointer(param_info)
        )

        if res != 0:
            self._raise_last_error("DSGetParamInfo")
        return param_info

    def DSMakeJobReport(
        self,
        job_name: JobHandle,
        report_type: ReportType,
        line_separator: Literal["CRLF", "LF", "CR"],
    ):
        """Generate a job report.

        Args:
            line_separator: Line separator in the report. The C API
                defaults to CRLF on Windows and LF on other platforms.
        """
        self._api.DSMakeJobReport.argtypes = [
            POINTER(DSJOB),
            c_int,
            c_char_p,
            POINTER(DSREPORTINFO),
        ]
        self._api.DSMakeJobReport.restype = c_int

        report_info = DSREPORTINFO()
        res = self._api.DSMakeJobReport(
            job_name,
            report_type,
            encode_string(line_separator),
            pointer(report_info),
        )

        if res != 0:
            self._raise_last_error("DSMakeJobReport")
        return report_info.info.reportText

    def DSGetReposUsage(
        self,
        project_name: ProjectHandle,
        relationship_type: ReposRelationshipType,
        object_name: str,
        recursive: int = 0,
    ):
        self._api.DSGetReposUsage.argtypes = [
            POINTER(DSPROJECT),
            c_int,
            c_char_p,
            c_int,
            POINTER(DSREPOSUSAGE),
        ]
        self._api.DSGetReposUsage.restype = c_int

        repos_usage = DSREPOSUSAGE()
        res = self._api.DSGetReposUsage(
            project_name,
            relationship_type,
            encode_string(object_name),
            recursive,
            pointer(repos_usage),
        )

        if res > 0:
            return repos_usage.info.jobs.contents
        if res == 0:
            return None
        self._raise_last_error("DSGetReposUsage")

    def DSGetReposInfo(
        self,
        project_name: ProjectHandle,
        object_type: ReposObjectType,
        info_type: ReposJobFilter,
        search_criteria: str,
        starting_category: str,
        subcategories: int = 1,
    ):
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
        res = self._api.DSGetReposInfo(
            project_name,
            object_type,
            info_type,
            encode_string(search_criteria),
            encode_string(starting_category),
            subcategories,
            pointer(repos_info),
        )

        if res > 0:
            return repos_info.info.jobs.contents
        if res == 0:
            return None
        self._raise_last_error("DSGetReposInfo")

    def DSLogEvent(
        self, job_name: JobHandle, event_type: LogEventType, message: str
    ) -> None:
        self._api.DSLogEvent.argtypes = [
            POINTER(DSJOB),
            c_int,
            c_char_p,
            c_char_p,
        ]
        self._api.DSLogEvent.restype = c_int

        res = self._api.DSLogEvent(
            job_name, event_type, encode_string(""), encode_string(message)
        )

        if res != 0:
            self._raise_last_error("DSLogEvent")

    def DSAddEnvVar(
        self,
        project_name: ProjectHandle,
        env_var_name: str,
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

        res = self._api.DSAddEnvVar(
            project_name,
            encode_string(env_var_name),
            encode_string(var_type),
            encode_string(prompt_text),
            encode_string(value),
        )

        if res != 0:
            self._raise_last_error("DSAddEnvVar")

    def DSDeleteEnvVar(
        self, project_name: ProjectHandle, env_var_name: str
    ) -> None:
        self._api.DSDeleteEnvVar.argtypes = [POINTER(DSPROJECT), c_char_p]
        self._api.DSDeleteEnvVar.restype = c_int

        res = self._api.DSDeleteEnvVar(
            project_name, encode_string(env_var_name)
        )

        if res != 0:
            self._raise_last_error("DSDeleteEnvVar")

    def DSSetEnvVar(
        self, project_name: ProjectHandle, env_var_name: str, value: str
    ) -> None:
        self._api.DSSetEnvVar.argtypes = [
            POINTER(DSPROJECT),
            c_char_p,
            c_char_p,
        ]
        self._api.DSSetEnvVar.restype = c_int

        res = self._api.DSSetEnvVar(
            project_name, encode_string(env_var_name), encode_string(value)
        )

        if res != 0:
            self._raise_last_error("DSSetEnvVar")

    def DSListEnvVars(self, project_name: ProjectHandle) -> list[str]:
        self._api.DSListEnvVars.argtypes = [POINTER(DSPROJECT)]
        self._api.DSListEnvVars.restype = POINTER(c_char)

        var_list = self._api.DSListEnvVars(project_name)

        if not var_list:
            self._raise_last_error("DSListEnvVars")
        return split_char_p(var_list)

    def DSAddProject(
        self, project_name: str, project_location: str = ""
    ) -> None:
        self._api.DSAddProject.argtypes = [c_char_p, c_char_p]
        self._api.DSAddProject.restype = c_int

        res = self._api.DSAddProject(
            encode_string(project_name), encode_string(project_location)
        )

        if res != 0:
            self._raise_last_error("DSAddProject")

    def DSDeleteProject(self, project_name: str) -> None:
        self._api.DSDeleteProject.argtypes = [c_char_p]
        self._api.DSDeleteProject.restype = c_int

        res = self._api.DSDeleteProject(encode_string(project_name))

        if res != 0:
            self._raise_last_error("DSDeleteProject")

    def DSGetIdForJob(self, project_name: ProjectHandle, job_name: str):
        self._api.DSGetIdForJob.argtypes = [POINTER(DSPROJECT), c_char_p]
        self._api.DSGetIdForJob.restype = c_char_p

        job_id = self._api.DSGetIdForJob(project_name, encode_string(job_name))

        if not job_id:
            self._raise_last_error("DSGetIdForJob")
        return job_id

    def DSSetIdForJob(
        self, project_name: ProjectHandle, job_name: str, job_id: str
    ) -> None:
        self._api.DSSetIdForJob.argtypes = [
            POINTER(DSPROJECT),
            c_char_p,
            c_char_p,
        ]
        self._api.DSSetIdForJob.restype = c_int

        res = self._api.DSSetIdForJob(
            project_name, encode_string(job_name), encode_string(job_id)
        )

        if res != 0:
            self._raise_last_error("DSSetIdForJob")

    def DSJobNameFromJobId(self, project_name: ProjectHandle, job_id: str):
        self._api.DSJobNameFromJobId.argtypes = [POINTER(DSPROJECT), c_char_p]
        self._api.DSJobNameFromJobId.restype = c_char_p

        job_name = self._api.DSJobNameFromJobId(
            project_name, encode_string(job_id)
        )

        if not job_name:
            self._raise_last_error("DSJobNameFromJobId")
        return job_name

    def DSServerMessage(
        self,
        def_msg: str,
        prms: list | None = None,
        msg_id_str: str = "",
        size_message: int = 1000,
    ):
        if prms is None:
            prms = []

        if not isinstance(prms, list):
            msg = "prms must be a list"
            raise TypeError(msg)

        max_prms = len(prms)

        self._api.DSServerMessage.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p * max_prms,
            c_char_p,
            c_int,
        ]
        self._api.DSServerMessage.restype = c_int

        encoded_prms = [encode_string(str(prm)) for prm in prms]
        res_message = c_char_p(encode_string(""))

        # TODO: `msg_size` not in use?
        msg_size = self._api.DSServerMessage(
            encode_string(msg_id_str),
            encode_string(def_msg),
            (c_char_p * max_prms)(*encoded_prms),
            res_message,
            size_message,
        )

        if not res_message:
            self._raise_last_error("DSServerMessage")
        return res_message.value

    def DSSetProjectProperty(
        self, project_name: ProjectHandle, property_name: str, value: str
    ) -> None:
        self._api.DSSetProjectProperty.argtypes = [
            POINTER(DSPROJECT),
            c_char_p,
            c_char_p,
        ]
        self._api.DSSetProjectProperty.restype = c_int

        res = self._api.DSSetProjectProperty(
            project_name, encode_string(property_name), encode_string(value)
        )

        if res != 0:
            self._raise_last_error("DSSetProjectProperty")

    def DSListProjectProperties(
        self, project_name: ProjectHandle
    ) -> list[str]:
        self._api.DSListProjectProperties.argtypes = [POINTER(DSPROJECT)]
        self._api.DSListProjectProperties.restype = POINTER(c_char)

        prop_list = self._api.DSListProjectProperties(project_name)

        if not prop_list:
            self._raise_last_error("DSListProjectProperties")
        return split_char_p(prop_list)

    def DSGetWLMEnabled(self) -> None:
        self._api.DSGetWLMEnabled.argtypes = []
        self._api.DSGetWLMEnabled.restype = c_int

        wlm_enabled = self._api.DSGetWLMEnabled()

        if not wlm_enabled:
            self._raise_last_error("DSGetWLMEnabled")

    def DSSetGenerateOpMetaData(self, job_name: JobHandle, value: int) -> None:
        self._api.DSSetGenerateOpMetaData.argtypes = [POINTER(DSJOB), c_int]
        self._api.DSSetGenerateOpMetaData.restype = c_int

        res = self._api.DSSetGenerateOpMetaData(job_name, value)

        if res != 0:
            self._raise_last_error("DSSetGenerateOpMetaData")

    def DSSetDisableProjectHandler(
        self, project_name: ProjectHandle, value: int
    ) -> None:
        self._api.DSSetDisableProjectHandler.argtypes = [
            POINTER(DSPROJECT),
            c_int,
        ]
        self._api.DSSetDisableProjectHandler.restype = c_int

        res = self._api.DSSetDisableProjectHandler(project_name, value)

        if res != 0:
            self._raise_last_error("DSSetDisableProjectHandler")

    def DSSetDisableJobHandler(self, job_name: JobHandle, value: int) -> None:
        self._api.DSSetDisableJobHandler.argtypes = [POINTER(DSJOB), c_int]
        self._api.DSSetDisableJobHandler.restype = c_int

        res = self._api.DSSetDisableJobHandler(job_name, value)

        if res != 0:
            self._raise_last_error("DSSetDisableJobHandler")

    def DSLoadLibrary(self, file: Path) -> None:
        """Load the DataStage API shared library.

        Args:
            file: Path to `vmdsapi.dll` (Windows)
                or `libvmdsapi.so` (UNIX).

        The relevant search-path variable must include the
        directory containing the library:

        - **Windows** — add the directory to `PATH`,
            typically `../IBM/InformationServer/Clients/Classic/`
        - **UNIX** — add the directory to `LD_LIBRARY_PATH`,
            typically `../IBM/InformationServer/Server/DSEngine/lib/`
        """
        if not file.is_file():
            msg = f"Library not found: {file!r}"
            raise FileNotFoundError(msg)

        try:
            self.__api = CDLL(file)
        except OSError as exc:
            msg = f"Cannot load the library: {exc!s}"
            raise OSError(msg) from exc

    def DSUnloadLibrary(self) -> None:
        self.__api = None
        self.__project_name = None
