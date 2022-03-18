from typing import List

import imageio
from bentoml import env, artifacts, api, BentoService
from bentoml.adapters import ImageInput
from bentoml.frameworks.pytorch import PytorchModelArtifact


@env(infer_pip_packages=True)
@artifacts([PytorchModelArtifact("model")])
class MnistTorchClassifier(BentoService):
    @api(input=ImageInput(), batch=False)
    def predict(self, image_array):
        results = self.artifacts.model.predict([image_array])
        return results[0]
