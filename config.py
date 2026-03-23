import os
import platformdirs
from enum import Enum, auto

from defaults import *


class ParamType(Enum):
    EMPTY = auto()
    NUMBER = auto()
    NUMBER_3 = auto()
    STRING = auto()
    FLOAT = auto()

class Config:
    """
    Bit convoluted but who cares
    """

    def __init__(self):
        self.config_dir_path = platformdirs.user_config_dir(
            APP_NAME,
            APP_AUTHOR
        )

        self.config_path = self.config_dir_path + "/" + "lyricify.conf"

        self.params = {
            "empty0": {"type": ParamType.EMPTY},

            "num_lines": {"type": ParamType.NUMBER, "value": 5},
            "font_size": {"type": ParamType.NUMBER, "value": 48},

            "empty1": {"type": ParamType.EMPTY},

            "active_scale": {"type": ParamType.NUMBER, "value": 11},
            "active_rotation": {"type": ParamType.NUMBER, "value": 4},

            "empty2": {"type": ParamType.EMPTY},

            "anchor_x": {"type": ParamType.NUMBER, "value": 192},
            "anchor_y": {"type": ParamType.NUMBER, "value": 540},
            "max_offset": {"type": ParamType.NUMBER, "value": 50},

            "empty3": {"type": ParamType.EMPTY},

            "noise_amount": {"type": ParamType.FLOAT, "value": 0.05},

            "empty4": {"type": ParamType.EMPTY},

            "use_local_cover_palette": {"type": ParamType.NUMBER, "value": 0, "comment": "set to 1 to use local music files for palette"},
            "music_file_path": {"type": ParamType.STRING, "value": "", "comment": "leave empty to use default Music directory"},

            "empty5": {"type": ParamType.EMPTY},

            "bg_color1": {"type": ParamType.NUMBER_3, "value": (56, 30, 60)},
            "bg_color2": {"type": ParamType.NUMBER_3, "value": (107, 89, 108)},
            "bg_color3": {"type": ParamType.NUMBER_3, "value": (200, 138, 151)},
            "text_color_dark": {"type": ParamType.NUMBER_3, "value": (209, 173, 212)},
            "text_color_light": {"type": ParamType.NUMBER_3, "value": (255, 239, 252)},
        }

        if not os.path.exists(self.config_dir_path):
            os.mkdir(self.config_dir_path)

        if not os.path.exists(self.config_path):
            self.gen_default_file()

        with open(self.config_path, "r") as file:
            if file.read() in ["", "\n"]:
                self.gen_default_file()

        self.load()

    def gen_default_file(self):
        file = open(self.config_path, "w")

        file.write("// auto generated config\n")

        for param, data in self.params.items():
            if data["type"] == ParamType.EMPTY:
                file.write("\n")
                continue

            if data["type"] == ParamType.STRING:
                value = '"' + str(data["value"]) + '"'
            else:
                value = str(data["value"])

            line = f"{param} = {value}"

            if "comment" in data:
                line += f" // {data["comment"]}"

            file.write(line + "\n")

        file.close()
        print(f"Generated default config file at {self.config_path}")

    def print_parse_error(self, line: int, comment: str):
        raise BaseException(f"Error parsing config at line {line}: {comment}")

    def load_param(self, line_idx: int, param: str, value):
        if param not in self.params:
            self.print_parse_error(line_idx, f"\"{param}\" doesn\'t exist.")

        match self.params[param]["type"]:
            case ParamType.NUMBER:
                self.params[param]["value"] = int(value)
            case ParamType.NUMBER_3:
                if not (value.count("(") == 1 and value.count(")") == 1):
                    self.print_parse_error(line_idx, "Syntax error.")

                value = value.lstrip("(").rstrip(")")
                numbers = [int(v) for v in value.split(",")]

                if len(numbers) != 3:
                    self.print_parse_error(line_idx, "Wrong number of values.")

                self.params[param]["value"] = tuple(numbers)
            case ParamType.STRING:
                if value.count('"') != 2:
                    self.print_parse_error(line_idx, "Syntax error.")

                value = value.strip('"')

                self.params[param]["value"] = value
            case ParamType.FLOAT:
                self.params[param]["value"] = float(value)

    def load(self):
        if not os.path.exists(self.config_path):
            raise BaseException("Couldn't load config.")

        file = open(self.config_path, "r")

        for line_idx, line in enumerate(file.read().split("\n")):
            line = line.replace(" ", "")

            if line.count("//"): # remove comment
                line = line[:line.index("//")]

            if not line.count("="):
                continue

            parts = line.split("=")

            if len(parts) < 2:
                raise BaseException(f"Error parsing config at line {line_idx}")

            param = parts[0]
            value = parts[1]

            self.load_param(line_idx, param, value)

        file.close()

    def __getitem__(self, item):
        if item in self.params:
            return self.params[item]["value"]

        raise BaseException(f"Config parameter couldn't be loaded: {item}. Is it defined in the config file?")