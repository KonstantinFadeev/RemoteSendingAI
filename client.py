import requests
import base64
from PIL import Image
from io import BytesIO
import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import datetime

from Inference.inference import Processor


def make_post_request(params):
    # Make a POST request with the parameters
    response = requests.post(url, data=params)
    if response.status_code == 200:
        json_data = response.json()
        encoded_images = json_data['images']
        image_list = []

        for encoded_image in encoded_images:
            # Decode the base64 encoded image
            decoded_data = base64.b64decode(encoded_image)
            # Create a BytesIO object to work with the binary data
            image_buffer = BytesIO(decoded_data)
            # Open the image using PIL
            image = Image.open(image_buffer)
            image_list.append(image)

        # Initialize an empty numpy array with the desired size
        result_array = np.empty((image_list[0].width, image_list[0].height, 12), dtype=np.uint8)

        # Convert each image to a numpy array and store it in the result array
        for i, img in enumerate(image_list[1:]):
            img_array = np.array(img)
            result_array[:, :, i*3:(i+1)*3] = img_array

        # The resulting array will have shape (12, n, m) where n is the height and m is the width of the images
        # Reshape the array to a 2D shape where the third dimension becomes the columns
        reshaped_array = np.reshape(result_array, (1024 * 1024, 12))

        # Convert the reshaped array to a DataFrame
        df = pd.DataFrame(reshaped_array).rename({0: 'Aerosol', 1: 'Blue', 2: 'Green', 3: 'Red', 4: 'IR1', 5: 'IR2', 6: 'IR3', 7: 'IR4', 8: 'IR5', 9: 'IR6', 10: 'IR7', 11: 'IR8'}, axis="columns")
        return df, image_list[0]
    else:
        return None, f'Request failed with status code: {response.status_code}'


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# Define the layout of the application
app.layout = html.Div(
    children=[
        html.H1("Система детектирования экологических проблем на основе мультиспектральных спутниковых изображений"),
        html.Div(
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            html.Label("X Coordinate:"),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            dbc.Input(id="x-input", type="number", value=137.029836),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            html.Label("Y Coordinate:"),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            dbc.Input(id="y-input", type="number", value=50.559578),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            html.Label("Length:"),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            dbc.Input(id="length-input", type="number", value=5),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            html.Label("Width:"),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            dbc.Input(id="width-input", type="number", value=5),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            html.Label("From:"),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id="date_from-picker",
                                display_format="YYYY-MM-DD",
                                date="2023-04-20",  # Initial value
                            ),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            html.Label("To:"),
                            width={"size": 2},
                        ),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id="date_to-picker",
                                display_format="YYYY-MM-DD",
                                date="2023-05-20",  # Initial value
                            ),
                            width={"size": 2},
                        ),
                    ],
                    className="mb-3",
                ),

                html.Button("Submit", id="submit-button"),
                dcc.Loading(
                    id="loading",
                    type="default",
                    children=[
                        html.Div(id='original-image'),
                        html.Div(
                            [html.Div(id='processed-image'),
                            html.Div(id='report', style={'width': '100%'})],
                            style={"display": "flex",
                                   'flex-direction': 'row'},
                        ),

                    ],
                ),
            ]
        ),
    ]
)


@app.callback(
    [Output('processed-image', 'children'),
     Output('original-image', 'children'),
     Output('report', 'children'),],
    [Input("submit-button", "n_clicks")],
    [
        dash.dependencies.State("x-input", "value"),
        dash.dependencies.State("y-input", "value"),
        dash.dependencies.State("length-input", "value"),
        dash.dependencies.State("width-input", "value"),
        dash.dependencies.State("date_from-picker", "date"),
        dash.dependencies.State("date_to-picker", "date"),
    ],
)
def process_request(n_clicks, x, y, length, width, date_from, date_to):
    if n_clicks is None:
        return ""

    # Format Dates
    date_from += ' 00:00:00'
    date_to += ' 23:59:59'
    date_from_obj = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
    date_to_obj = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
    date_from = date_from_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_to = date_to_obj.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Send a POST request with the provided parameters
    params = {"x": x, "y": y, "length": length, "width": width, "date_from": date_from, "date_to": date_to}
    data, rgb_image = make_post_request(params)
    result_view, result_report = process_area(data, rgb_image.height, rgb_image.width)
    report_text = '''
        Данные анализа изображений:
        - Широта: {}
        - Долгота: {}
        - Размер области: {}км
        '''.format(x, y, (length, width))

    original_image = [ html.H3('Оригинальное изображение:'),
                                    html.Img(style={"width": "20%"}, src=rgb_image)]
    result_image_output = [
        html.H3('Обработанное изображение:'),
        html.Img(style={"width": "100%"}, src=Image.fromarray(result_view))
    ]

    report = [html.H3('Отчет:'),
              dcc.Markdown(children=report_text),
              # dcc.Graph(figure=result_report[0]),
              dcc.Graph(figure=result_report, )]

    return [result_image_output, original_image, report]


def process_area(data, h, w):
    processor = Processor(data=data, input_image_shape=(w,h))
    return processor.process()


if __name__ == '__main__':
    url = 'http://localhost:5000/get_images'  # Replace with the appropriate URL
    app.run_server(debug=True)

