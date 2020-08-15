from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar('T')

class DefaultResponse(GenericModel, Generic[T]):
    hasError:bool
    success:bool

    data: Optional[T] = None


class ErrorData(GenericModel, Generic[T]):
    error_msg:str
    errors: List[T] = None

