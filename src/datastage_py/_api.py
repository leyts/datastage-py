"""High-level wrapper classes for the IBM DataStage API."""

from datetime import timedelta
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from datastage_py._constants import (
    JobInfoType,
    JobStatus,
    LinkInfoType,
    ProjectInfoType,
    StageInfoType,
)
from datastage_py.utils import (
    decode_bytes,
    parse_null_separated,
    timestamp_to_datetime,
)

if TYPE_CHECKING:
    from datetime import datetime
    from types import TracebackType
    from typing import Self

    from datastage_py._bindings import DSAPI, JobHandle, ProjectHandle
    from datastage_py._structures import (
        DSJOBINFO,
        DSLINKINFO,
        DSPROJECTINFO,
        DSSTAGEINFO,
    )


class Server:
    """High-level entry point for a DataStage server."""

    def __init__(
        self,
        api: DSAPI,
        *,
        domain_name: str | None = None,
        server_name: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Initialise the server wrapper."""
        self._api = api
        if domain_name is not None:
            self._api.DSSetServerParams(
                domain_name,
                server_name,
                username,
                password,
            )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(api={self._api!r})"

    @property
    def api(self) -> DSAPI:
        """Low-level API instance."""
        return self._api

    @property
    def list_projects(self) -> list[str]:
        """List all projects on the server."""
        return self._api.DSGetProjectList()

    def open_project(self, name: str) -> Project:
        """Open a project handle and return a :class:`Project` instance."""
        handle = self._api.DSOpenProject(name)
        return Project(self._api, handle)


class Project:
    """A DataStage project."""

    def __init__(self, api: DSAPI, handle: ProjectHandle) -> None:
        self._api = api
        self._handle = handle
        self._closed = False

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the project handle."""
        self.close()

    @property
    def handle(self) -> ProjectHandle:
        """Raw project handle."""
        return self._handle

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
        info = self._get_info(ProjectInfoType.HOSTNAME)
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
    def list_jobs(self) -> list[str]:
        """List all jobs in the project."""
        info = self._get_info(ProjectInfoType.JOB_LIST)
        return parse_null_separated(info.info.jobList)

    def open_job(self, name: str) -> Job:
        """Open a job handle and return a :class:`Job` instance."""
        handle = self._api.DSOpenJob(self._handle, name)
        return Job(self._api, handle)

    def close(self) -> None:
        """Close the project. Safe to call multiple times."""
        if self._closed:
            return
        self._api.DSCloseProject(self._handle)
        self._closed = True

    def _get_info(self, info_type: ProjectInfoType) -> DSPROJECTINFO:
        return self._api.DSGetProjectInfo(self._handle, info_type)


class Job:
    """A DataStage job."""

    def __init__(self, api: DSAPI, handle: JobHandle) -> None:
        self._api = api
        self._handle = handle
        self._closed = False

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the job handle."""
        self.close()

    @property
    def handle(self) -> JobHandle:
        """Raw job handle."""
        return self._handle

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
        """Job status."""
        info = self._get_info(JobInfoType.STATUS)
        return JobStatus(info.info.jobStatus)

    @property
    def interim_status(self) -> JobStatus:
        """Job status after all stages run, before the after-job subroutine."""
        info = self._get_info(JobInfoType.INTERIM_STATUS)
        return JobStatus(info.info.jobInterimStatus)

    @property
    def user_status(self) -> str:
        """Job user status."""
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
    def pid(self) -> int:
        """Job process ID."""
        info = self._get_info(JobInfoType.PID)
        return int(info.info.jobPid)

    @property
    def controller(self) -> str:
        """Controlling job name."""
        info = self._get_info(JobInfoType.CONTROLLER)
        return decode_bytes(info.info.jobController)

    @property
    def wave_number(self) -> int:
        """Wave number of the last or current run."""
        info = self._get_info(JobInfoType.WAVE_NUMBER)
        return int(info.info.jobWaveNumber)

    @property
    def short_description(self) -> str:
        """Job short description from the `Job Properties` dialogue."""
        info = self._get_info(JobInfoType.DESCRIPTION)
        return decode_bytes(info.info.jobDesc)

    @property
    def full_description(self) -> str:
        """Job full description from the `Job Properties` dialogue."""
        info = self._get_info(JobInfoType.FULL_DESCRIPTION)
        return decode_bytes(info.info.jobFullDesc)

    @property
    def list_parameters(self) -> list[str]:
        """List all job parameter names."""
        info = self._get_info(JobInfoType.PARAMETER_LIST)
        return parse_null_separated(info.info.paramList)

    @property
    def list_stages(self) -> list[str]:
        """List all active job stages."""
        info = self._get_info(JobInfoType.STAGE_LIST)
        return parse_null_separated(info.info.stageList)

    @property
    def list_invocations(self) -> list[str]:
        """List all job invocation names."""
        info = self._get_info(JobInfoType.INVOCATIONS)
        return parse_null_separated(info.info.jobInvocations)

    @property
    def is_stop_requested(self) -> bool:
        """Whether a stop request has been issued for the job."""
        info = self._get_info(JobInfoType.CONTROL)
        return bool(info.info.jobControl)

    @property
    def is_web_service(self) -> bool:
        """Whether this is a web (DMI) service job."""
        info = self._get_info(JobInfoType.DMI_SERVICE)
        return bool(info.info.jobDMIService)

    @property
    def is_multi_instance(self) -> bool:
        """Whether this job supports multiple instances (invocations)."""
        info = self._get_info(JobInfoType.MULTI_INVOKABLE)
        return bool(info.info.jobMultiInvokable)

    @property
    def is_restartable(self) -> bool:
        """Whether this job can be restarted."""
        info = self._get_info(JobInfoType.RESTARTABLE)
        return bool(info.info.jobRestartable)

    def open_stage(self, name: str) -> Stage:
        """Return a :class:`Stage` instance for a given stage."""
        return Stage(self._api, self._handle, name)

    def close(self) -> None:
        """Close the job. Safe to call multiple times."""
        if self._closed:
            return
        self._api.DSCloseJob(self._handle)
        self._closed = True

    def _get_info(self, info_type: JobInfoType) -> DSJOBINFO:
        return self._api.DSGetJobInfo(self._handle, info_type)


class Stage:
    """A stage within a DataStage job."""

    def __init__(self, api: DSAPI, handle: JobHandle, name: str) -> None:
        self._api = api
        self._handle = handle
        self._name = name

    @cached_property
    def name(self) -> str:
        """Stage name."""
        info = self._get_info(StageInfoType.NAME)
        return decode_bytes(info.info.stageName)

    @property
    def stage_type(self) -> str:
        """Stage type (e.g. Transformer, BeforeJob)."""
        info = self._get_info(StageInfoType.TYPE)
        return decode_bytes(info.info.typeName)

    @property
    def description(self) -> str:
        """Stage description."""
        info = self._get_info(StageInfoType.DESCRIPTION)
        return decode_bytes(info.info.stageDesc)

    @property
    def status(self) -> int:
        """Stage status."""
        info = self._get_info(StageInfoType.STATUS)
        return int(info.info.stageStatus)

    @property
    def start_time(self) -> datetime:
        """Stage start timestamp."""
        info = self._get_info(StageInfoType.START_TIMESTAMP)
        return timestamp_to_datetime(info.info.stageStartTime)

    @property
    def finish_time(self) -> datetime:
        """Stage finish timestamp."""
        info = self._get_info(StageInfoType.END_TIMESTAMP)
        return timestamp_to_datetime(info.info.stageEndTime)

    @property
    def elapsed_time(self) -> timedelta:
        """Stage elapsed time."""
        info = self._get_info(StageInfoType.ELAPSED)
        return timedelta(seconds=int(decode_bytes(info.info.stageElapsed)))

    @property
    def row_count(self) -> int:
        """Primary link input row count."""
        info = self._get_info(StageInfoType.IN_ROW_NUM)
        return int(info.info.inRowNum)

    @property
    def list_instances(self) -> list[str]:
        """List all instance names (parallel jobs)."""
        info = self._get_info(StageInfoType.INSTANCES)
        return parse_null_separated(info.info.instList)

    @property
    def list_pids(self) -> list[int]:
        """List all process IDs (parallel jobs)."""
        info = self._get_info(StageInfoType.PID)
        return [int(s) for s in parse_null_separated(info.info.pidList)]

    @property
    def list_cpu_times(self) -> list[timedelta]:
        info = self._get_info(StageInfoType.CPU)
        return [
            timedelta(seconds=int(s))
            for s in parse_null_separated(info.info.cpuList)
        ]

    @property
    def list_links(self) -> list[str]:
        """List all link names."""
        info = self._get_info(StageInfoType.LINK_LIST)
        return parse_null_separated(info.info.linkList)

    @property
    def list_link_types(self) -> list[str]:
        """List all link types."""
        info = self._get_info(StageInfoType.LINK_TYPES)
        return parse_null_separated(info.info.linkTypes)

    @property
    def list_variables(self) -> list[str]:
        """List all stage variable names."""
        info = self._get_info(StageInfoType.VARIABLE_LIST)
        return parse_null_separated(info.info.varList)

    @property
    def custom_info(self) -> list[str]:
        info = self._get_info(StageInfoType.CUST_INFO_LIST)
        return parse_null_separated(info.info.custInfoList)

    def open_link(self, name: str) -> Link:
        """Return a :class:`Link` instance for a given link."""
        return Link(self._api, self._handle, self._name, name)

    def _get_info(self, info_type: StageInfoType) -> DSSTAGEINFO:
        return self._api.DSGetStageInfo(self._handle, self._name, info_type)


class Link:
    """A link to or from a stage within a DataStage job."""

    def __init__(
        self, api: DSAPI, handle: JobHandle, stage_name: str, name: str
    ) -> None:
        self._api = api
        self._handle = handle
        self._stage_name = stage_name
        self._name = name

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
        info = self._get_info(LinkInfoType.DESCRIPTION)
        return decode_bytes(info.info.linkDesc)

    @property
    def stage(self) -> str:
        """Name of the stage at the other end of the link."""
        info = self._get_info(LinkInfoType.STAGE)
        return decode_bytes(info.info.linkedStage)

    def _get_info(self, info_type: LinkInfoType) -> DSLINKINFO:
        return self._api.DSGetLinkInfo(
            self._handle, self._stage_name, self._name, info_type
        )
