from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Frame, Meta


class IFrameSource(ABC):
    @abstractmethod
    def start(self) -> None: ...
    @abstractmethod
    def read(self) -> tuple[Frame, Meta] | None: ...
    @abstractmethod
    def stop(self) -> None: ...


class IPipelineStage(ABC):
    @abstractmethod
    def process(self, frame: Frame, meta: Meta) -> tuple[Any, Meta]: ...


class IFrameSink(ABC):
    @abstractmethod
    def push(self, item: Frame, meta: Meta) -> None: ...
    @abstractmethod
    def close(self) -> None: ...
    @abstractmethod
    def connect(self, slot: callable) -> None: ...
