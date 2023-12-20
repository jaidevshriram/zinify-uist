class SimpleFirstPageConfig:
    with open("html_templates/pages/simple_first_page.html", "r") as file:
        html = file.read()

    image_count = 1
    texts = ["short"]


class SimpleSecondPageConfig:
    with open("html_templates/pages/simple_second_page.html", "r") as file:
        html = file.read()

    image_count = 0
    texts = ["long"]


class SimpleThirdPageConfig:
    with open("html_templates/pages/simple_third_page.html", "r") as file:
        html = file.read()

    image_count = 1
    texts = ["short", "short"]


class SimpleFourthPageConfig:
    with open("html_templates/pages/simple_fourth_page.html", "r") as file:
        html = file.read()

    image_count = 1
    texts = ["short", "long"]


class SimpleFifthPageConfig:
    with open("html_templates/pages/simple_fifth_page.html", "r") as file:
        html = file.read()

    image_count = 0
    texts = ["long"]


class SimpleSixthPageConfig:
    with open("html_templates/pages/simple_sixth_page.html", "r") as file:
        html = file.read()

    image_count = 1
    texts = ["long"]


class Page:
    def __init__(self, config):
        self.config = config
        self.html = config.html

    def render(self, image_paths, texts):
        for i in range(len(texts)):
            self.html = self.config.replace(f"text_filler_{i}", texts[i])
        for i in range(len(image_paths)):
            self.html = self.html.replace(f"image_filler_{i}", image_paths[i])
        return self.html


class ZineLayout:
    def __init__(self, pages):
        self.pages = pages
        with open("html_templates/layout.html", "r") as file:
            self.html = file.read()

    def render(self, zine):
        """
        zine: ZineContent object
        """
        contents = zine.pages
        assert len(contents) == len(self.pages)

        for i in range(len(contents)):
            page = self.pages[i]
            content = contents[i]
            image_paths = content["image_paths"]
            texts = content["texts"]
            self.html = self.html.replace(f"page_{i}", page.render(image_paths, texts))
        return self.html


SimpleLayoutTemplate = ZineLayout(
    [
        Page(SimpleFirstPageConfig),
        Page(SimpleSecondPageConfig),
        Page(SimpleThirdPageConfig),
        Page(SimpleFourthPageConfig),
        Page(SimpleFifthPageConfig),
        Page(SimpleSixthPageConfig),
    ]
)
