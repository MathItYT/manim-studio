from manim import *


config.pixel_width = 1280
config.pixel_height = 640
config.frame_width = config.frame_height * \
    config.pixel_width / config.pixel_height


class ManimStudio(Scene):
    # add_guide = True
    add_guide = False

    def construct(self):
        banner = ManimBanner()
        studio = Tex("Studio")
        studio.scale(4)

        if self.add_guide:
            guide = ImageMobject("repository-open-graph-template.png")
            guide.scale_to_fit_height(config.frame_height)
            self.add(guide)

        vg = VGroup(banner, studio).arrange(RIGHT, buff=0.5)
        studio.set_y(banner.M.get_bottom()[1] + studio.get_height() / 2)
        self.add(vg)


class ManimStudioLight(Scene):
    add_guide = False

    def construct(self):
        banner = ManimBanner(dark_theme=False)
        studio = Tex("Studio", color=DARKER_GRAY)
        studio.scale(4)

        if self.add_guide:
            guide = ImageMobject("repository-open-graph-template.png")
            guide.scale_to_fit_height(config.frame_height)
            self.add(guide)

        vg = VGroup(banner, studio).arrange(RIGHT, buff=0.5)
        studio.set_y(banner.M.get_bottom()[1] + studio.get_height() / 2)
        self.add(vg)
