"""High-level wrapper classes for the IBM DataStage API."""

from datetime import timedelta
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

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
    from datetime import datetime
    from types import TracebackType
    from typing import Self

    from datastage_py.datastage import DSAPI, JobHandle, ProjectHandle
    from datastage_py.structures import (
        DSJOBINFO,
        DSLINKINFO,
        DSPROJECTINFO,
        DSSTAGEINFO,
    )


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

    @cached_property
    def name(self) -> str:
        """Project name."""
        info = self._get_info(ProjectInfoType.NAME)
        return decode_bytes(info.info.projectName)

    @cached_property
    def path(self) -> Path:
        """Project directory path."""
        info = self._get_info(ProjectInfoType.PATH)
        return Path(decode_bytes(info.info.projectPath))

    @cached_property
    def hostname(self) -> str:
        """Engine hostname."""
        info = self._get_info(ProjectInfoType.HOST_NAME)
        return decode_bytes(info.info.hostName)

    @cached_property
    def install_tag(self) -> str:
        """Engine installation tag."""
        info = self._get_info(ProjectInfoType.INSTALL_TAG)
        return decode_bytes(info.info.installTag)

    @cached_property
    def tcp_port(self) -> int:
        """Engine TCP port."""
        info = self._get_info(ProjectInfoType.TCP_PORT)
        return int(info.info.tcpPort)

    @property
    def jobs(self) -> list[str]:
        """Job names in the project."""
        info = self._get_info(ProjectInfoType.JOB_LIST)
        return split_char_p(info.info.jobList)

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

    @cached_property
    def name(self) -> str:
        """Job name."""
        info = self._get_info(JobInfoType.NAME)
        return decode_bytes(info.info.jobName)

    @property
    def invocation_id(self) -> str:
        """Job invocation name."""
        info = self._get_info(JobInfoType.INVOCATION_ID)
        return decode_bytes(info.info.jobInvocationId)

    @property
    def status(self) -> JobStatus:
        """Current job status."""
        info = self._get_info(JobInfoType.STATUS)
        return JobStatus(info.info.jobStatus)

    @property
    def interim_status(self) -> JobStatus:
        """Status after all stages have run, before the after-job subroutine."""  # noqa: E501
        info = self._get_info(JobInfoType.INTERIM_STATUS)
        return JobStatus(info.info.jobInterimStatus)

    @property
    def user_status(self) -> str:
        """Job user status, if any."""
        info = self._get_info(JobInfoType.USER_STATUS)
        return decode_bytes(info.info.userStatus)

    @property
    def start_time(self) -> datetime:
        """Job start timestamp."""
        info = self._get_info(JobInfoType.START_TIMESTAMP)
        return timestamp_to_datetime(info.info.jobStartTime)

    @property
    def finish_time(self) -> datetime:
        """Job finish timestamp."""
        info = self._get_info(JobInfoType.LAST_TIMESTAMP)
        return timestamp_to_datetime(info.info.jobLastTime)

    @property
    def elapsed_time(self) -> timedelta:
        """Job elapsed time."""
        info = self._get_info(JobInfoType.ELAPSED)
        return timedelta(seconds=info.info.jobElapsed)

    @property
    def controller(self) -> str:
        """Controlling job name."""
        info = self._get_info(JobInfoType.CONTROLLER)
        return decode_bytes(info.info.jobController)

    @property
    def pid(self) -> int:
        info = self._get_info(JobInfoType.PID)
        return int(info.info.jobPid)

    @property
    def wave_number(self) -> int:
        """Wave number of the last or current run."""
        info = self._get_info(JobInfoType.WAVE_NO)
        return int(info.info.jobWaveNumber)

    @property
    def short_description(self) -> str:
        """Description from the `Job Properties` dialogue."""
        info = self._get_info(JobInfoType.DESC)
        return decode_bytes(info.info.jobDesc)

    @property
    def full_description(self) -> str:
        """Full description from the `Job Properties` dialogue."""
        info = self._get_info(JobInfoType.FULL_DESC)
        return decode_bytes(info.info.jobFullDesc)

    @property
    def parameters(self) -> list[str]:
        """Job parameter names."""
        info = self._get_info(JobInfoType.PARAM_LIST)
        return split_char_p(info.info.paramList)

    @property
    def stages(self) -> list[str]:
        """Active job stages."""
        info = self._get_info(JobInfoType.STAGE_LIST)
        return split_char_p(info.info.stageList)

    @property
    def invocation_ids(self) -> list[str]:
        """Job invocation names."""
        info = self._get_info(JobInfoType.INVOCATIONS)
        return split_char_p(info.info.jobInvocations)

    @property
    def is_stop_requested(self) -> int:
        """Whether a stop request has been issued for the job."""
        info = self._get_info(JobInfoType.CONTROL)
        return int(info.info.jobControl)

    @property
    def is_web_service(self) -> bool:
        """Whether this is a web (DMI) service job."""
        info = self._get_info(JobInfoType.DMI_SERVICE)
        return bool(info.info.jobDMIService)

    @property
    def is_multi_invokable(self) -> bool:
        """Whether this job supports multiple invocations."""
        info = self._get_info(JobInfoType.MULTI_INVOKABLE)
        return bool(info.info.jobMultiInvokable)

    @property
    def is_restartable(self) -> bool:
        """Whether this job can be restarted."""
        info = self._get_info(JobInfoType.RESTARTABLE)
        return bool(info.info.jobRestartable)

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

    @cached_property
    def name(self) -> str:
        info = self._get_info(StageInfoType.NAME)
        return decode_bytes(info.info.stageName)

    @property
    def type_name(self) -> str:
        info = self._get_info(StageInfoType.TYPE)
        return decode_bytes(info.info.typeName)

    @property
    def links(self) -> list[str]:
        info = self._get_info(StageInfoType.LINK_LIST)
        return split_char_p(info.info.linkList)

    @property
    def link_types(self) -> list[str]:
        info = self._get_info(StageInfoType.LINK_TYPES)
        return split_char_p(info.info.linkTypes)

    @property
    def variables(self) -> list[str]:
        info = self._get_info(StageInfoType.VAR_LIST)
        return split_char_p(info.info.varList)

    @property
    def row_count(self) -> int:
        info = self._get_info(StageInfoType.IN_ROW_NUM)
        return int(info.info.inRowNum)

    @property
    def start_time(self) -> datetime:
        info = self._get_info(StageInfoType.START_TIMESTAMP)
        return timestamp_to_datetime(info.info.stageStartTime)

    @property
    def end_time(self) -> datetime:
        info = self._get_info(StageInfoType.END_TIMESTAMP)
        return timestamp_to_datetime(info.info.stageEndTime)

    @property
    def description(self) -> str:
        info = self._get_info(StageInfoType.DESC)
        return decode_bytes(info.info.stageDesc)

    @property
    def instances(self) -> list[str]:
        info = self._get_info(StageInfoType.INST)
        return split_char_p(info.info.instList)

    @property
    def cpu(self) -> list[str]:
        info = self._get_info(StageInfoType.CPU)
        return split_char_p(info.info.cpuList)

    @property
    def elapsed(self) -> str:
        info = self._get_info(StageInfoType.ELAPSED)
        return decode_bytes(info.info.stageElapsed)

    @property
    def pids(self) -> list[str]:
        info = self._get_info(StageInfoType.PID)
        return split_char_p(info.info.pidList)

    @property
    def status(self) -> int:
        info = self._get_info(StageInfoType.STATUS)
        return int(info.info.stageStatus)

    @property
    def custom_info(self) -> list[str]:
        info = self._get_info(StageInfoType.CUST_INFO_LIST)
        return split_char_p(info.info.custInfoList)

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

    @cached_property
    def name(self) -> str:
        info = self._get_info(LinkInfoType.NAME)
        return decode_bytes(info.info.linkName)

    @property
    def row_count(self) -> int:
        info = self._get_info(LinkInfoType.ROW_COUNT)
        return int(info.info.rowCount)

    @property
    def sql_state(self) -> str:
        info = self._get_info(LinkInfoType.SQL_STATE)
        return decode_bytes(info.info.linkSQLState)

    @property
    def dbms_code(self) -> str:
        info = self._get_info(LinkInfoType.DBMS_CODE)
        return decode_bytes(info.info.linkDBMSCode)

    @property
    def description(self) -> str:
        info = self._get_info(LinkInfoType.DESC)
        return decode_bytes(info.info.linkDesc)

    @property
    def stage(self) -> str:
        info = self._get_info(LinkInfoType.STAGE)
        return decode_bytes(info.info.linkedStage)
