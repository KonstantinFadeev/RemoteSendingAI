import pickle
import plotly.express as px
from dataclasses import dataclass
from typing import Tuple, List

import pandas as pd

import numpy as np

from Inference.constants import FEATURES, COLORS_MAPPING, INT_TO_CLASS


@dataclass
class Processor:
    data: pd.DataFrame
    input_image_shape: Tuple[int, int]

    def process(self):
        model_base, model_plant, model_water = self._get_models()
        result = []
        base_predictions = model_base.predict(self.data[FEATURES["base_model"]])
        water_predictions = model_base.predict(self.data[FEATURES["model_water"]])
        plant_predictions = model_base.predict(self.data[FEATURES["model_plant"]])

        for i in range(len(base_predictions)):
            base_prediction = base_predictions[i]
            if base_prediction == 1:
                prediction = INT_TO_CLASS["water"][water_predictions[i][0]]
            elif base_prediction == 3:
                prediction = INT_TO_CLASS["plant"][plant_predictions[i][0]]
            else:
                prediction = INT_TO_CLASS["general"][base_prediction[0]]

            result.append(prediction)

        report = self._get_report(result)
        result_image = np.empty((self.input_image_shape[0], self.input_image_shape[1], 3), dtype=np.uint8)
        for index_y in range(self.input_image_shape[1]):
            for index_x in range(self.input_image_shape[0]):
                pixel_prediction = result[index_x*self.input_image_shape[1] + index_y]
                result_image[index_x, index_y] = COLORS_MAPPING['all_rgb'][pixel_prediction]

        return result_image, report

    def _get_models(self):
        models = []
        with open(
                self.path_to_models[0],
                "rb") as model_file:

            models.append(pickle.load(model_file))

        with open(
                self.path_to_models[1],
                "rb") as model_file:

            models.append(pickle.load(model_file))

        with open(
                self.path_to_models[2],
                "rb") as model_file:

            models.append(pickle.load(model_file))
        return models

    def _get_report(self, prediction):
        df = pd.DataFrame(prediction).rename({0: "class"}, axis="columns")
        statistics = dict()
        for class_name in df["class"].unique():
            statistics[class_name] = len(df[df["class"] == class_name])
        df = pd.Series(statistics).reset_index().rename({"index": "class", 0: "count"}, axis="columns")
        df['Color'] = df['class'].map(COLORS_MAPPING["all"])

        fig = px.pie(
                df,
                values='count',
                names='class',
                title='Сводный отчет о состоянии земной поверхности',
                color_discrete_sequence=df['Color'])
        fig.update_layout(
            margin=dict(t=20, b=20, r=20, l=20),
            autosize=True
        )
        return fig




