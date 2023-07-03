import json
import pprint
from abc import abstractmethod, ABCMeta
from typing import Optional, List

import yaml
from pydantic import BaseModel, StrictStr, StrictInt, Field


class ExtendedBaseModel(BaseModel, metaclass=ABCMeta):
    class Config:
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str):
        return cls.from_dict(json.loads(json_str))

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict())

    @classmethod
    def from_yaml(cls, yaml_str: str):
        return cls.from_dict(yaml.safe_load(yaml_str))

    def to_dict(self) -> dict:
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    @abstractmethod
    def from_dict(cls, obj: Optional[dict]) -> Optional:
        raise NotImplementedError()


class SingleRegistration(ExtendedBaseModel):
    instance_url: StrictStr
    runner_token: StrictStr
    runner_name: StrictStr

    @classmethod
    def from_dict(cls, obj: Optional[dict]) -> Optional['SingleRegistration']:
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return SingleRegistration.parse_obj(obj)

        _obj = SingleRegistration.parse_obj({
            "instance_url": obj.get("instance_url"),
            "runner_token": obj.get("runner_token"),
            "runner_name": obj.get("runner_name"),
        })
        return _obj


class RegistrationConfiguration(ExtendedBaseModel):
    instances: List[SingleRegistration] = list()

    @classmethod
    def from_dict(cls, obj: Optional[dict]) -> Optional['RegistrationConfiguration']:
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return RegistrationConfiguration.parse_obj(obj)

        _obj = RegistrationConfiguration.parse_obj({
            "instances": obj.get("instances"),
        })
        return _obj


class InstanceInfo(ExtendedBaseModel):
    instance_url: StrictStr
    registration_token: StrictStr

    @classmethod
    def from_dict(cls, obj: Optional[dict]) -> Optional['InstanceInfo']:
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return InstanceInfo.parse_obj(obj)

        _obj = InstanceInfo.parse_obj({
            "instance_url": obj.get("instance_url"),
            "registration_token": obj.get("registration_token"),
        })
        return _obj


class ApplicationConfiguration(ExtendedBaseModel):
    runner_name: StrictStr
    instances: List[InstanceInfo]
    concurrency: StrictInt
    description: Optional[StrictStr] = None
    ssl_verification: Optional[bool] = Field(True)
    tmp_dir: StrictStr

    @classmethod
    def default(cls) -> 'ApplicationConfiguration':
        return cls(
            runner_name='TODO',
            instances=[InstanceInfo(instance_url='TODO',
                                    registration_token='ptrrt-TODO')],
            concurrency=2,
            description='Example description',
            ssl_verification=True,
            tmp_dir='./tmp',
        )

    @classmethod
    def from_dict(cls, obj: Optional[dict]) -> Optional['ApplicationConfiguration']:
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return ApplicationConfiguration.parse_obj(obj)

        _obj = ApplicationConfiguration.parse_obj({
            "instances": obj.get("instances"),
            "runner_name": obj.get("runner_name"),
            "concurrency": obj.get("concurrency"),
            "description": obj.get("description"),
            "ssl_verification": obj.get("ssl_verification"),
            "tmp_dir": obj.get("tmp_dir"),
        })
        return _obj
