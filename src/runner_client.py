import logging
import os.path
from typing import Optional, List

import requests
from barkeputils import human_readable_filesize_base_10
from peertube_api_client import ApiClient, Configuration, ApiV1RunnersRegisterPostRequest, \
    ApiV1RunnersRegisterPost200Response, ApiV1RunnersUnregisterPostRequest, RunnerJobsApi, RunnersApi, \
    ApiV1RunnersJobsRequestPost200ResponseAvailableJobsInner, \
    ApiV1RunnersJobsJobUUIDAcceptPost200Response, ApiV1RunnersJobsJobUUIDAbortPostRequest, \
    ApiV1RunnersJobsJobUUIDUpdatePostRequest, ApiV1RunnersJobsJobUUIDUpdatePostRequestPayload


class RunnerClient:
    def __init__(self, instance_url: str, name: str, description: str, registration_token: str,
                 verify_ssl: bool = True):
        self.logger = logging.getLogger(RunnerClient.__module__ + '.' + RunnerClient.__name__)
        self.name = name
        self.description = description
        self.instance_url = instance_url
        self.registration_token = registration_token
        self.verify_ssl = verify_ssl
        self.runner_token: Optional[str] = None
        config = Configuration(host=self.instance_url)
        config.verify_ssl = verify_ssl
        self.api_client = ApiClient(config)
        self.runner_jobs_api = RunnerJobsApi(self.api_client)
        self.runners_api = RunnersApi(self.api_client)
        # Disable annoying warnings if user specifically told to ignore ssl verification errors
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def request_a_new_job(self) -> List[ApiV1RunnersJobsRequestPost200ResponseAvailableJobsInner]:
        if self.runner_token is None:
            self.register()

        jobs = self.runner_jobs_api.api_v1_runners_jobs_request_post(
            ApiV1RunnersUnregisterPostRequest(
                runner_token=self.runner_token,
            )
        ).available_jobs

        if len(jobs) != 0:
            self.logger.info(f'Got {len(jobs)} available job(s)')

        return jobs

    def accept_job(self, job_uuid: str) -> ApiV1RunnersJobsJobUUIDAcceptPost200Response:
        if self.runner_token is None:
            self.register()

        self.logger.info(f'Accepting a job: {job_uuid}')

        return self.runner_jobs_api.api_v1_runners_jobs_job_uuid_accept_post(
            job_uuid=job_uuid,
            api_v1_runners_unregister_post_request=ApiV1RunnersUnregisterPostRequest(
                runner_token=self.runner_token
            )
        )

    def abort_job(self, job_uuid: str, job_token: str, reason: str):
        if self.runner_token is None:
            self.register()

        self.logger.info(f'Aborting a job: {job_uuid}')

        self.runner_jobs_api.api_v1_runners_jobs_job_uuid_abort_post(
            job_uuid=job_uuid,
            api_v1_runners_jobs_job_uuid_abort_post_request=ApiV1RunnersJobsJobUUIDAbortPostRequest(
                runner_token=self.runner_token,
                job_token=job_token,
                reason=reason
            )
        )

    def get_video(self, url: str, output_dir: str, job_token: str) -> str:
        filename = os.path.join(output_dir, job_token)
        self.logger.debug(f'Downloading a video to {filename} for a job {job_token}')
        data = {'runnerToken': self.runner_token, 'jobToken': job_token}
        total_bytes_downloaded = 0
        with requests.post(url, stream=True, data=data, verify=self.verify_ssl) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    total_bytes_downloaded += len(chunk)
        self.logger.debug('Downloaded a video to %s for a job %s with a size of %s',
                          filename, job_token, human_readable_filesize_base_10(total_bytes_downloaded))
        return filename

    def register(self) -> str:
        self.logger.info(f'Registering runner for instance {self.instance_url}')
        rs: ApiV1RunnersRegisterPost200Response = self.runners_api.api_v1_runners_register_post(
            ApiV1RunnersRegisterPostRequest(
                registration_token=self.registration_token,
                name=self.name,
                description=self.description,
            )
        )
        self.runner_token = rs.runner_token

        return self.runner_token

    def update_job(
            self,
            job_uuid: str,
            job_token: str,
            progress: Optional[int] = None,
            payload: Optional[ApiV1RunnersJobsJobUUIDUpdatePostRequestPayload] = None
    ):
        self.logger.info(f'Updating job progress for instance {self.instance_url} for a job {job_token}')

        self.runner_jobs_api.api_v1_runners_jobs_job_uuid_update_post(
            job_uuid=job_uuid,
            api_v1_runners_jobs_job_uuid_update_post_request=ApiV1RunnersJobsJobUUIDUpdatePostRequest(
                job_token=job_token,
                runner_token=self.runner_token,
                progress=progress,
                payload=payload
            )
        )

    def unregister(self):
        self.logger.info(f'Unregistering runner for instance {self.instance_url}')
        self.runners_api.api_v1_runners_unregister_post(
            ApiV1RunnersUnregisterPostRequest(
                runner_token=self.runner_token,
            )
        )
