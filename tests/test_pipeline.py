import numpy as np
from core.pipeline.base import Pipeline
from core.pipeline.stages.canny import CannyStage
from core.api.types import Meta

def test_canny_stage_shapes():
    img = (np.random.rand(240, 320, 3)*255).astype(np.uint8)
    pipe = Pipeline([CannyStage()])
    out, meta = pipe.run_once(img, Meta(0))
    assert out.shape == img.shape
