"""High-level wrapper classes for the IBM DataStage API."""

from typing import TYPE_CHECKING, Self

from datastage_py.enums import (
    JobInfoType,
    JobStatus,
    LinkInfoType,
    ProjectInfoType,
    StageInfoType,
)
from datastage_py.utils import (
    decode_bytes,
    split_char_p,
    timestamp_to_datetime,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from enum import IntEnum
    from types import TracebackType

    from datastage_py.datastage import DSAPI, JobHandle, ProjectHandle
    from datastage_py.structures import (
        DSJOBINFO,
        DSLINKINFO,
        DSPROJECTINFO,
        DSSTAGEINFO,
    )


def _info_property(
    info_type: IntEnum, field: str, converter: Callable[..., object]
) -> property:
    """Descriptor that extracts and converts a single info field."""

    def fget(self: Project | Job | Stage | Link) -> object:
        info = self._get_info(info_type)  # type: ignore[invalid-argument-type]
        return converter(getattr(info.info, field))

    return property(fget)


class Project:
    """Pythonic wrapper around a DataStage project handle."""

    def __init__(self, api: DSAPI, handle: ProjectHandle) -> None:
        """Wrap an already-opened project handle."""
        self._api = api
        self._handle = handle

    def __enter__(self) -> Self:
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the project handle."""
        self._api.DSCloseProject(self._handle)

    def _get_info(self, info_type: ProjectInfoType) -> DSPROJECTINFO:
        return self._api.DSGetProjectInfo(self._handle, info_type)

    name = _info_property(
        ProjectInfoType.NAME,
        "projectName",
        decode_bytes,
    )
    path = _info_property(
        ProjectInfoType.PATH,
        "projectPath",
        decode_bytes,
    )
    host_name = _info_property(
        ProjectInfoType.HOST_NAME,
        "hostName",
        decode_bytes,
    )
    install_tag = _info_property(
        ProjectInfoType.INSTALL_TAG,
        "installTag",
        decode_bytes,
    )
    tcp_port = _info_property(
        ProjectInfoType.TCP_PORT,
        "tcpPort",
        decode_bytes,
    )
    jobs = _info_property(
        ProjectInfoType.JOB_LIST,
        "jobList",
        split_char_p,
    )

    def open_job(self, name: str) -> Job:
        """Open a job by name and return a :class:`Job` wrapper."""
        handle = self._api.DSOpenJob(self._handle, name)
        return Job(self._api, handle)


class Job:
    """Pythonic wrapper around a DataStage job handle."""

    def __init__(self, api: DSAPI, handle: JobHandle) -> None:
        """Wrap an already-opened job handle."""
        self._api = api
        self._handle = handle

    def __enter__(self) -> Self:
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the job handle."""
        self._api.DSCloseJob(self._handle)

    def _get_info(self, info_type: JobInfoType) -> DSJOBINFO:
        return self._api.DSGetJobInfo(self._handle, info_type)

    status = _info_property(
        JobInfoType.STATUS,
        "jobStatus",
        JobStatus,
    )
    name = _info_property(
        JobInfoType.NAME,
        "jobName",
        decode_bytes,
    )
    controller = _info_property(
        JobInfoType.CONTROLLER,
        "jobController",
        decode_bytes,
    )
    start_time = _info_property(
        JobInfoType.START_TIMESTAMP,
        "jobStartTime",
        timestamp_to_datetime,
    )
    last_time = _info_property(
        JobInfoType.LAST_TIMESTAMP,
        "jobLastTime",
        timestamp_to_datetime,
    )
    wave_number = _info_property(
        JobInfoType.WAVE_NO,
        "jobWaveNumber",
        int,
    )
    params = _info_property(
        JobInfoType.PARAM_LIST,
        "paramList",
        split_char_p,
    )
    stages = _info_property(
        JobInfoType.STAGE_LIST,
        "stageList",
        split_char_p,
    )
    user_status = _info_property(
        JobInfoType.USER_STATUS,
        "userStatus",
        decode_bytes,
    )
    control = _info_property(
        JobInfoType.CONTROL,
        "jobControl",
        int,
    )
    pid = _info_property(
        JobInfoType.PID,
        "jobPid",
        int,
    )
    invocations = _info_property(
        JobInfoType.INVOCATIONS,
        "jobInvocations",
        split_char_p,
    )
    interim_status = _info_property(
        JobInfoType.INTERIM_STATUS,
        "jobInterimStatus",
        JobStatus,
    )
    invocation_id = _info_property(
        JobInfoType.INVOCATION_ID,
        "jobInvocationId",
        decode_bytes,
    )
    description = _info_property(
        JobInfoType.DESC,
        "jobDesc",
        decode_bytes,
    )
    full_description = _info_property(
        JobInfoType.FULL_DESC,
        "jobFullDesc",
        decode_bytes,
    )
    elapsed = _info_property(
        JobInfoType.ELAPSED,
        "jobElapsed",
        int,
    )
    dmi_service = _info_property(
        JobInfoType.DMI_SERVICE,
        "jobDMIService",
        int,
    )
    multi_invokable = _info_property(
        JobInfoType.MULTI_INVOKABLE,
        "jobMultiInvokable",
        bool,
    )
    restartable = _info_property(
        JobInfoType.RESTARTABLE,
        "jobRestartable",
        bool,
    )

    def open_stage(self, name: str) -> Stage:
        """Return a :class:`Stage` wrapper for the given stage."""
        return Stage(self._api, self._handle, name)


class Stage:
    """Pythonic wrapper around DataStage stage info queries."""

    def __init__(self, api: DSAPI, job_handle: JobHandle, name: str) -> None:
        """Wrap stage info access for the given stage name."""
        self._api = api
        self._job_handle = job_handle
        self._name = name

    def _get_info(self, info_type: StageInfoType) -> DSSTAGEINFO:
        return self._api.DSGetStageInfo(
            self._job_handle, self._name, info_type
        )

    name = _info_property(
        StageInfoType.NAME,
        "stageName",
        decode_bytes,
    )
    type_name = _info_property(
        StageInfoType.TYPE,
        "typeName",
        decode_bytes,
    )
    links = _info_property(
        StageInfoType.LINK_LIST,
        "linkList",
        split_char_p,
    )
    link_types = _info_property(
        StageInfoType.LINK_TYPES,
        "linkTypes",
        split_char_p,
    )
    variables = _info_property(
        StageInfoType.VAR_LIST,
        "varList",
        split_char_p,
    )
    row_count = _info_property(
        StageInfoType.IN_ROW_NUM,
        "inRowNum",
        int,
    )
    start_time = _info_property(
        StageInfoType.START_TIMESTAMP,
        "stageStartTime",
        timestamp_to_datetime,
    )
    end_time = _info_property(
        StageInfoType.END_TIMESTAMP,
        "stageEndTime",
        timestamp_to_datetime,
    )
    description = _info_property(
        StageInfoType.DESC,
        "stageDesc",
        decode_bytes,
    )
    instances = _info_property(
        StageInfoType.INST,
        "instList",
        split_char_p,
    )
    cpu = _info_property(
        StageInfoType.CPU,
        "cpuList",
        split_char_p,
    )
    elapsed = _info_property(
        StageInfoType.ELAPSED,
        "stageElapsed",
        decode_bytes,
    )
    pids = _info_property(
        StageInfoType.PID,
        "pidList",
        split_char_p,
    )
    status = _info_property(
        StageInfoType.STATUS,
        "stageStatus",
        int,
    )
    custom_info = _info_property(
        StageInfoType.CUST_INFO_LIST,
        "custInfoList",
        split_char_p,
    )

    def open_link(self, name: str) -> Link:
        """Return a :class:`Link` wrapper for the given link."""
        return Link(self._api, self._job_handle, self._name, name)


class Link:
    """Pythonic wrapper around DataStage link info queries."""

    def __init__(
        self, api: DSAPI, job_handle: JobHandle, stage_name: str, name: str
    ) -> None:
        """Wrap link info access for the given link name."""
        self._api = api
        self._job_handle = job_handle
        self._stage_name = stage_name
        self._name = name

    def _get_info(self, info_type: LinkInfoType) -> DSLINKINFO:
        return self._api.DSGetLinkInfo(
            self._job_handle, self._stage_name, self._name, info_type
        )

    name = _info_property(
        LinkInfoType.NAME,
        "linkName",
        decode_bytes,
    )
    row_count = _info_property(
        LinkInfoType.ROW_COUNT,
        "rowCount",
        int,
    )
    sql_state = _info_property(
        LinkInfoType.SQL_STATE,
        "linkSQLState",
        decode_bytes,
    )
    dbms_code = _info_property(
        LinkInfoType.DBMS_CODE,
        "linkDBMSCode",
        decode_bytes,
    )
    description = _info_property(
        LinkInfoType.DESC,
        "linkDesc",
        decode_bytes,
    )
    stage = _info_property(
        LinkInfoType.STAGE,
        "linkedStage",
        decode_bytes,
    )
