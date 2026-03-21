from PIL import Image
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score
import os
import pyray as pr


class Gradient:
    def __init__(self, screen_size: tuple[int, int]):
        self.shader = pr.load_shader("", "shaders/gradient.frag")
        self.colors = [
            0.5, 0.4, 0,
            0, 0, 0,
            0.5, 0.3, 0.2
        ]
        # self.colors = [
        #     1, 0, 0,
        #     0, 1, 0,
        #     0, 0, 1
        # ]

        value = pr.ffi.new("float[]", self.colors)
        pr.set_shader_value_v(
            self.shader,
            pr.get_shader_location(self.shader, "colors"),
            value,
            pr.ShaderUniformDataType.SHADER_UNIFORM_VEC3,
            len(self.colors)
        )

        # aspect ratio
        value = pr.ffi.new("float*", screen_size[0] / screen_size[1])
        pr.set_shader_value(
            self.shader,
            pr.get_shader_location(self.shader, "aspectRatio"),
            value,
            pr.ShaderUniformDataType.SHADER_UNIFORM_FLOAT
        )

        # fix shader rect bug using this (don't ask me how)
        texture = pr.Texture(
            pr.rl_get_texture_id_default(),
            1, 1,
            1,
            pr.PixelFormat.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8
        )
        pr.set_shapes_texture(
            texture,
            (0, 0, 1, 1)
        )

    def from_image(self, path: str):
        if not os.path.exists(path):
            return

        image = Image.open(path)
        pixels = list(image.getdata())

        result = QuantizeCelebi(pixels, 128)
        colors = Score.score(result)

        print(colors)

    def render(self, screen_size: tuple[int, int]):
        pr.begin_shader_mode(self.shader)

        pr.draw_rectangle(
            0, 0,
            *screen_size,
            pr.WHITE
        )

        pr.end_shader_mode()