class ZineContent:
    def __init__(self, zine_layout, callback=None):
        self.summary = None
        self.pages = [None]*len(zine_layout.pages)
        self.layout_config = zine_layout
        self.callback = callback

    def _trigger_callback(self):
        if self.callback:
            self.callback(self.zine_content)

    def add_summary(self,  summary):
        self.summary = summary
        self._trigger_callback()

    def add_page_content(self, i, page_content):
        self.pages[i] = page_content
        self._trigger_callback()

    def update_image_path(self, i, image_paths):
        self.pages[i]["image_paths"] = image_paths
        self._trigger_callback()

    def render(self):
        return self.layout_config.render(self)

        