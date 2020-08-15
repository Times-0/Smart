from typing import Optional, TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar('T')

class DefaultResponse(BaseModel, Generic[T]):
    hasError:bool
    success:bool

    data: Optional[T] = None


class ErrorData(BaseModel, Generic[T]):
    error_msg:str
    errors: List[T] = None

