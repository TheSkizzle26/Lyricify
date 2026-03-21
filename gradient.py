import pyray as pr

from palette import Palette


class Gradient:
    def __init__(self, palette: Palette, screen_size: tuple[int, int]):
        self.palette = palette
        self.num_colors = 3

        self.shader = pr.load_shader("", "shaders/gradient.frag")
        self.upload_colors()

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

    def upload_colors(self):
        colors = []
        for i in range(self.num_colors):
            [colors.append(v) for v in self.palette.get_color_float(i)]

        value = pr.ffi.new("float[]", colors)
        pr.set_shader_value_v(
            self.shader,
            pr.get_shader_location(self.shader, "colors"),
            value,
            pr.ShaderUniformDataType.SHADER_UNIFORM_VEC3,
            len(colors)
        )

    def render(self, screen_size: tuple[int, int]):
        pr.begin_shader_mode(self.shader)

        self.upload_colors()
        pr.draw_rectangle(
            0, 0,
            *screen_size,
            pr.WHITE
        )

        pr.end_shader_mode()