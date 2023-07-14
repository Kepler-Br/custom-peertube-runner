from abc import ABC, abstractmethod
from typing import Set

from peertube_api_client import VODWebVideoTranscoding1Input, VODWebVideoTranscoding1Output, RunnerJobType, \
    ApiV1RunnersJobsJobUUIDAcceptPost200ResponseJob


class AbstractEncoderJob(ABC):
    @abstractmethod
    def can_accept(self, inp: VODWebVideoTranscoding1Input, out: VODWebVideoTranscoding1Output,
                   job_type: RunnerJobType) -> bool:
        pass

    @abstractmethod
    def get_supported_job_types(self) -> Set[RunnerJobType]:
        pass

    @abstractmethod
    def transcode(self, job: ApiV1RunnersJobsJobUUIDAcceptPost200ResponseJob, source_file: str, target_dir: str) -> str:
        pass
