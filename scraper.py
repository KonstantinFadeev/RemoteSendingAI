from flask import Flask, request, make_response
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from PIL import Image
from io import BytesIO
import base64
import json

app = Flask(__name__)


def km_to_coordinate(km):
    return round((1 / 111.32) * km, 6)


def build_rectangle(latitude, longitude, length_km, width_km):
    # Расчет половин длины и ширины
    half_length = km_to_coordinate(length_km / 2)
    half_width = km_to_coordinate(width_km / 2)

    # Расчет координат углов прямоугольника
    top_left = (latitude + half_width, longitude - half_length)
    bottom_right = (latitude - half_width, longitude + half_length)

    # Возвращаем угловые точки прямоугольника
    return top_left, bottom_right


@app.route('/image', methods=['GET', 'POST'])
def image():
    # Get the x and y coordinates from the request data
    # x = int(request.form.get('x', 0))
    # y = int(request.form.get('y', 0))
    # length = int(request.form.get('length', 0))
    # width = int(request.form.get('width', 0))
    x = 137.029836
    y = 50.559578
    length = 5
    width = 5

    bbox = build_rectangle(x, y, length, width)
    json_data = {
                  "input": {
                      "bounds": {
                          "bbox": [
                              bbox[0][0],
                              bbox[0][1],
                              bbox[1][0],
                              bbox[1][1],
                          ]
                      },
                      "data": [{
                          "dataFilter": {
                              "timeRange": {
                                  "from": "2023-04-20T00:00:00Z",
                                  "to": "2023-05-20T23:59:59Z"
                              },
                              "maxCloudCoverage": 10
                          },
                          "type": "sentinel-2-l2a"
                      }]
                  },
                  "output": {
                      "width": 1024,
                      "height": 1024,
                      "responses": [
                          {
                              "identifier": "default",
                              "format": {
                                  "type": "image/jpeg"
                              }
                          }
                      ]
                  },
                  "evalscript": """
                        //VERSION=3
                
                        function setup() {
                          return {
                            input: ["#B3#", "#B2#", "#B1#"],
                            output: {
                              bands: 3
                            }
                          };
                        }
                
                        function evaluatePixel(
                          sample,
                          scenes,
                          inputMetadata,
                          customData,
                          outputMetadata
                        ) {
                          return [2.5 * sample.#B1#, 2.5 * sample.#B2#, 2.5 * sample.#B3#];
                        }
                        """
                }

    bands = (('B04', 'B03', 'B02'),
             ('B01', 'B02', 'B03'),
             ('B04', 'B05', 'B06'),
             ('B07', 'B08', 'B09'),
             ('B11', 'B12', 'B8A'))

    images_content = []
    for bandGroup in bands:
        json_data_copy = replace_bands(bandGroup, json_data)
        response = oauth.post('https://services.sentinel-hub.com/api/v1/process', json=json_data_copy)
        base64_data = base64.b64encode(response.content).decode('utf-8')
        images_content.append(base64_data)
    return {'images': images_content}


def replace_bands(band_group, json_data):
    json_data_copy = json_data.copy()
    json_data_copy['evalscript'] = json_data_copy['evalscript'].replace('#B1#', band_group[0])
    json_data_copy['evalscript'] = json_data_copy['evalscript'].replace('#B2#', band_group[1])
    json_data_copy['evalscript'] = json_data_copy['evalscript'].replace('#B3#', band_group[2])
    return json_data_copy


def authenticate():
    global oauth, token

    # Your client credentials
    client_id = '9f323316-6a44-4302-bb1b-ad5572fe1c20'
    client_secret = 'u8K}VI|^sq2jOj~FZkk.<EDUF!a7_*Clm|/.s>5K'

    # Create a session
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)

    # Get token for the session
    token = oauth.fetch_token(token_url='https://services.sentinel-hub.com/oauth/token',
                              client_secret=client_secret)

    # All requests using this session will have an access token automatically added
    resp = oauth.get("https://services.sentinel-hub.com/oauth/tokeninfo")
    print(resp.content)

    def sentinelhub_compliance_hook(response):
        response.raise_for_status()
        return response

    oauth.register_compliance_hook("access_token_response", sentinelhub_compliance_hook)


if __name__ == '__main__':
    authenticate()
    app.run(debug=True)
