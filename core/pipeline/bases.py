from __future__ import annotations
from typing import Iterable, Any
from core.api.interfaces import IPipelineStage
from core.api.types import Frame, Meta

class Pipeline:
    def __init__(self, stages: Iterable[IPipelineStage]):
        self.stages = list(stages)

    def run_once(self, frame: Frame, meta: Meta) -> tuple[Any, Meta]:
        data: Any = frame
        m = meta
        for st in self.stages:
            data, m = st.process(data, m)
        return data, m
