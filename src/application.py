import logging
import os
import os.path
import os.path
import pathlib

from config_models import ApplicationConfiguration, RegistrationConfiguration
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
            accepted = client.accept_job(jobs[0].uuid)
            # 'ptrjt-c0bb6dbd-1e80-4ef5-9a5b-36e803e9b929'
            client.abort_job(job_uuid=jobs[0].uuid, job_token=accepted.job.job_token, reason='Testing')
            client.unregister()

    def run(self):
        self._register_runner()
