from manim_studio import *
from manim import *


class ManimStudioLogo(VGroup):
    def __init__(self):
        self.banner = ManimBanner()
        self.studio = Tex("Studio")
        self.studio.scale(4)
        super().__init__(self.banner, self.studio)
        self.arrange(RIGHT, buff=0.5)
        self.studio.set_y(self.banner.M.get_bottom()[
                          1] + self.studio.get_height() / 2)

    @override_animation(Create)
    def create(self):
        return AnimationGroup(Create(self.banner), LaggedStartMap(FadeIn, self.studio, scale=2))

    @override_animate(Uncreate)
    def uncreate(self):
        return FadeOut(self, scale=5)


class ManimStudioPresentation(LiveScene):
    def presentation_intro(self):
        self.logo = ManimStudioLogo()
        self.play(Create(self.logo))
        self.pause_slide()

        self.play(self.logo.animate.scale_to_fit_width(2.5).to_corner(DR))
        self.pause_slide()

        self.title = Text("Manim Studio First Presentation")
        self.author = Text("by @CodeIt_YT")
        self.title_page = VGroup(self.title, self.author)
        self.title_page.arrange(DOWN)

        self.play(DrawBorderThenFill(self.title_page))
        self.pause_slide()

    def whats_manim_studio(self):
        self.what_is_it = Text("What is Manim Studio?").scale(2)
        self.play(FadeOut(self.title_page, scale=5), FadeIn(self.what_is_it))
        self.pause_slide()

        self.answer = Text("Manim Studio is basically a GUI for Manim.", t2s={
                           "basically": ITALIC})
        self.play(LaggedStart(self.what_is_it.animate.to_corner(
            UL), FadeIn(self.answer), lag_ratio=0.5))
        self.pause_slide()

        self.is_it_all = Text("Is it all?", weight=BOLD).to_edge(DOWN)
        self.play(FadeIn(self.is_it_all))
        self.pause_slide()

        self.yes_joke = Text("Yes, it is all.\nThanks for watching!", t2w={
                             "Yes": BOLD}, t2c={"Thanks for watching": YELLOW}).scale(2)
        self.play(FadeOut(self.answer), FadeOut(self.is_it_all),
                  FadeIn(self.yes_joke))
        self.pause_slide()

        self.its_a_joke = Text("It's a joke, of course.", t2w={
            "joke": BOLD}).scale(2)
        self.play(FadeOut(self.yes_joke), FadeIn(self.its_a_joke))
        self.pause_slide()

    def whats_manim_studio_2(self):
        self.github_description = Text(
            "\"A GUI to easier make Manim animations\"", t2w={"easier": BOLD}).scale(1.5)
        self.play(FadeTransform(self.its_a_joke, self.github_description))
        self.pause_slide()

        self.github_link = Text(
            "https://github.com/MathItYT/manim-studio").next_to(self.github_description, DOWN)
        self.github_link.set_color(GREY)
        self.play(Write(self.github_link))
        self.pause_slide()

    def features(self):
        self.play(FadeOut(self.what_is_it), FadeOut(
            self.github_description), FadeOut(self.github_link))

    def construct(self):
        self.presentation_intro()
        self.whats_manim_studio()
        self.whats_manim_studio_2()
        self.features()
        super().construct()
