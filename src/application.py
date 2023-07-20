import base64
import logging
import os
import os.path
import os.path
import pathlib

from peertube_api_client import ApiV1RunnersJobsJobUUIDUpdatePostRequestPayload

from config_models import ApplicationConfiguration, RegistrationConfiguration
from encoders.h264_encoder_job import H265EncoderJob
from exceptions import ApplicationStartUpError
from runner_client import RunnerClient


class ApplicationBuilder:
    config_file_name = 'config.yaml'
    instances_file_name = 'instances.yaml'

    def __init__(self, config_dir: str):
        self.config_dir = config_dir

    def build(self) -> 'Application':
        self._check_dirs_and_configs_and_create_dirs()
        config = self._load_config()
        instance_config = self._load_instance_config()
        self._create_tmp(tmp_dir=config.tmp_dir)

        return Application(config_dir=self.config_dir, config=config, instances=instance_config)

    def _load_config(self) -> ApplicationConfiguration:
        config_path = os.path.join(self.config_dir, self.config_file_name)
        if not os.path.exists(config_path):
            config = ApplicationConfiguration.default()
            with open(config_path, 'w') as fp:
                fp.write(config.to_yaml())
            raise ApplicationStartUpError(f'A default configuration on path "{config_path}" is created. '
                                          f'Please, configure and start again')
        with open(config_path, 'r') as fp:
            config = ApplicationConfiguration.from_yaml(fp.read())

        if config.runner_name == 'TODO':
            raise ApplicationStartUpError(f'runner_name is "{config.runner_name}". '
                                          f'Have you changed your configuration at "{config_path}"?')
        if len(config.instances) == 0:
            raise ApplicationStartUpError(f'No instances configured under config path "instances:". '
                                          f'Delete {config_path} to get a default config '
                                          f'if don\'t know config structure.')

        if len(config.instances) == 0:
            raise ApplicationStartUpError(f'No instances configured in {config_path}')

        return config

    def _check_dirs_and_configs_and_create_dirs(self):
        # Create config dir
        if os.path.exists(self.config_dir) and not os.path.isdir(self.config_dir):
            raise ApplicationStartUpError(f'{self.config_dir} is not a directory')
        if not os.path.exists(self.config_dir):
            pathlib.Path(self.config_dir).mkdir(parents=True)

        config_path = os.path.join(self.config_dir, self.config_file_name)
        if os.path.exists(config_path):
            if not os.access(config_path, os.R_OK):
                raise ApplicationStartUpError(f'{config_path} is not readable')
            if not os.path.isfile(config_path):
                raise ApplicationStartUpError(f'{config_path} is not a file')

        instance_config_path = os.path.join(self.config_dir, self.instances_file_name)
        if os.path.exists(instance_config_path):
            if not os.access(instance_config_path, os.W_OK | os.R_OK):
                raise ApplicationStartUpError(f'{instance_config_path} is not read/write')
            if not os.path.isfile(instance_config_path):
                raise ApplicationStartUpError(f'{instance_config_path} is not a file')

    def _load_instance_config(self) -> RegistrationConfiguration:
        config_path = os.path.join(self.config_dir, self.instances_file_name)

        if not os.path.exists(config_path):
            return RegistrationConfiguration()

        with open(config_path, 'r') as fp:
            return RegistrationConfiguration.from_yaml(fp.read())

    @staticmethod
    def _create_tmp(tmp_dir: str):
        if os.path.isfile(tmp_dir):
            raise ApplicationStartUpError(f'{tmp_dir} is not a directory')
        if os.path.exists(tmp_dir) and not os.access(tmp_dir, os.W_OK | os.R_OK):
            raise ApplicationStartUpError(f'{tmp_dir} is not read/write')

        pathlib.Path(tmp_dir).mkdir(parents=True, exist_ok=True)


class Application:
    instances_file_name = 'instances.yaml'

    def __init__(self, config_dir: str, config: ApplicationConfiguration, instances: RegistrationConfiguration):
        self.config_dir = config_dir
        self.config = config
        self.instances = instances
        self.logger = logging.getLogger(Application.__module__ + '.' + Application.__name__)

    @staticmethod
    def builder(config_dir: str) -> ApplicationBuilder:
        return ApplicationBuilder(config_dir=config_dir)

    def _register_runner(self):
        for it in self.config.instances:
            client = RunnerClient(instance_url=it.instance_url,
                                  name=self.config.runner_name,
                                  description=self.config.description,
                                  registration_token=it.registration_token,
                                  verify_ssl=self.config.ssl_verification)
            client.register()
            jobs = client.request_a_new_job()
            if len(jobs) == 0:
                self.logger.error('No jobs received')
                return
            accepted = client.accept_job(jobs[0].uuid)
            video_file = client.get_video(url=accepted.job.payload.actual_instance.input.video_file_url,
                                          output_dir=self.config.tmp_dir, job_token=accepted.job.job_token)
            transcode_job = H265EncoderJob().transcode_generator(job=accepted.job, target_dir=self.config.tmp_dir,
                                                                 input_video=video_file)
            while True:
                try:
                    next(transcode_job)
                    client.update_job(job_uuid=jobs[0].uuid, job_token=accepted.job.job_token)
                except StopIteration as ex:
                    output_video_file = ex.value
                    break
            with open(output_video_file, 'rb') as fp:

                client.post_success_vod_web(
                    job_uuid=jobs[0].uuid,
                    job_token=accepted.job.job_token,
                    video_file=base64.b64encode(fp.read())
                )
            # while True:
            #     with open(output_video_file, 'rb') as fp:
            #         video_chunk = fp.read(1024 * 100)
            #         if len(video_chunk) == 0:
            #             break
            #         client
            #         client.update_job(
            #             job_uuid=jobs[0].uuid,
            #             job_token=accepted.job.job_token,
            #             payload=ApiV1RunnersJobsJobUUIDUpdatePostRequestPayload(
            #                 video_chunk_file=base64.b64encode(video_chunk).decode('UTF-8'),
            #                 video_chunk_filename=output_video_file
            #             )
            #         )

            os.remove(video_file)
            client.abort_job(job_uuid=jobs[0].uuid, job_token=accepted.job.job_token, reason='Testing')
            client.unregister()

    def run(self):
        self._register_runner()
