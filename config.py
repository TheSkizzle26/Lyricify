import os
from asyncio.events import BaseDefaultEventLoopPolicy

import platformdirs
from enum import Enum, auto

from defaults import *


class ParamType:
    NUMBER = auto()
    NUMBER_3 = auto()
    FLOAT = auto()

class Config:
    def __init__(self):
        self.config_dir_path = platformdirs.user_config_dir(
            APP_NAME,
            APP_AUTHOR
        )

        self.config_path = self.config_dir_path + "/" + "lyricify.conf"

        self.params = {
            "num_lines": {"type": ParamType.NUMBER, "value": 5},
            "font_size": {"type": ParamType.NUMBER, "value": 48},
            "active_scale": {"type": ParamType.NUMBER, "value": 11},
            "active_rotation": {"type": ParamType.NUMBER, "value": 4},
            "anchor_x": {"type": ParamType.NUMBER, "value": 192},
            "anchor_y": {"type": ParamType.NUMBER, "value": 540},
            "max_offset": {"type": ParamType.NUMBER, "value": 50},
            "noise_amount": {"type": ParamType.FLOAT, "value": 0.05},
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
            file.write(f"{param} = {str(data["value"])}\n")

        file.close()
        print(f"Generated default config file at {self.config_path}")

    def load_param(self, line_idx: int, param: str, value):
        if param not in self.params:
            raise BaseException(f"Error parsing config at line {line_idx}: '{param}' doesn't exist.")

        match self.params[param]["type"]:
            case ParamType.NUMBER:
                self.params[param]["value"] = int(value)
            case ParamType.NUMBER_3:
                value = value.lstrip("(").rstrip(")")
                numbers = [int(v) for v in value.split(",")]

                if len(numbers) != 3:
                    raise BaseException(f"Error parsing config at line {line_idx}: Wrong number of values.")

                self.params[param]["value"] = tuple(numbers)
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