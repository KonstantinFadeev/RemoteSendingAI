PATH_TO_MODELS = ["path_to_base_model.pickle", "path_to_wather_model.pickle", "path_to_plant_model.pickle"]

FEATURES = {
    "base_model": ["Red", "IR8"],
    "model_water": ["Red", "IR8"],
    "model_plant": ["Red", "IR8"],
}

INT_TO_CLASS = {
    "all": {
        1: "Здоровая растительность",
        2: "Угнетенная растительность",
        3: "Чистая вода",
        4: "Морская вода",
        5: "Цветущая вода",
        6: "Грязная вода",
        7: "Нефтепродукт на воде",
        8: "Антропогенные объекты",
        9: "Почва",
    },
    "general": {
        1: "Вода",
        2: "Почва",
        3: "Растительность",
        4: "Антропогенные объекты",
    },
    "plant": {
        1: "Здоровая растительность",
        2: "Угнетенная растительность",
    },
    "water": {
        1: "Чистая вода",
        2: "Нефтепродукт на воде",
        3: "Цветущая вода",
        4: "Грязная вода",
    },

}

COLORS_MAPPING = {
    "all": {
        'Здоровая растительность': '#3D0B51',
        'Угнетенная растительность': '#3F5287',
        "Чистая вода": '#46528B',
        "Морская вода": '#FFFF00',
        "Цветущая вода": "#0000FF",
        "Грязная вода": "#00FF00",
        "Нефтепродукт на воде": "#FF00FF",
        "Антропогенные объекты": '#FF0055',
        "Почва": '#FF0000',
    },
    'all_rgb':{
        'Здоровая растительность': [61, 11, 81],
        'Угнетенная растительность': [63, 82, 135],
        'Чистая вода': [70, 82, 139],
        'Морская вода': [255, 255, 0],
        'Цветущая вода': [0, 0, 255],
        'Грязная вода': [0, 255, 0],
        'Нефтепродукт на воде': [255, 0, 255],
        "Антропогенные объекты": [255, 0, 85],
        'Почва': [255, 0, 0]
    }
}
