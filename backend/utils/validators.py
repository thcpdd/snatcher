from datetime import datetime

from bson import ObjectId as BSONObjectId
from pydantic import BaseModel
from pydantic_core import core_schema


class ObjectId(BSONObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _):
        if isinstance(v, BSONObjectId):
            return ObjectId(v)
        if isinstance(v, str) and BSONObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Id must be of type ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        json_schema = handler(schema)
        json_schema.update(
            type="string",
            example="66629e539ea1c08c80765e0a",
        )
        return json_schema

    @classmethod
    def __get_pydantic_core_schema__(cls, _, __):
        return core_schema.json_or_python_schema(
            python_schema=core_schema.with_info_plain_validator_function(cls.validate),
            json_schema=core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: str(instance)),
        )


class DatetimeValidator(BaseModel):
    def model_dump(self, *args, **kwargs) -> dict:
        dump = super().model_dump(*args, **kwargs)
        for k, v in dump.items():
            if isinstance(v, datetime):
                dump[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        return dump
