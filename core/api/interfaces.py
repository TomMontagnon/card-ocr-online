from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Any
from .types import Frame, Meta

class IFrameSource(ABC):
    @abstractmethod
    def start(self) -> None: ...
    @abstractmethod
    def read(self) -> Optional[tuple[Frame, Meta]]: ...
    @abstractmethod
    def stop(self) -> None: ...

class IPipelineStage(ABC):
    @abstractmethod
    def process(self, frame: Frame, meta: Meta) -> tuple[Any, Meta]: ...

class IFrameSink(ABC):
    @abstractmethod
    def push(self, item: Any, meta: Meta) -> None: ...
