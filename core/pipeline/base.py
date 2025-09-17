from __future__ import annotations
from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.api.types import Frame, Meta
    from core.api.interfaces import IPipelineStage
    from collections.abc import Iterable


class Pipeline:
    def __init__(self, stages: Iterable[IPipelineStage]) -> None:
        self.stages = list(stages)

    def run_once(self, frame: Frame, meta: Meta) -> (Frame, Meta):
        data: Any = frame
        m = meta
        for st in self.stages:
            data, m = st.process(data, m)
        return data, m
