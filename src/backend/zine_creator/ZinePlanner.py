from ..llm_conversation import ClaudeConversation
from ..prompt_templates import *
from .ZineContent import ZineContent
import multiprocessing


class ZinePlanner:
    def __init__(self, pdf_text, style, content_type, zine_content, callback=None):
        self.pdf_text = pdf_text
        self.style = style
        self.content_type = content_type
        # self.conversation = ClaudeConversation()
        self.zine_content = zine_content  # ZineContent object
        self.layoutConfig = zine_content.layout_config
        self.callback = callback
        # self.zine_plan_conversation = None
        # self.page_plans = [None] * len(self.layoutConfig.pages)

    def _trigger_callback(self):
        if self.callback:
            self.callback(self.zine_content)

    def split_into_pages(self, plan_text):
        # Placeholder; You'll need to implement this
        raise NotImplementedError

    def split_into_content(self, plan_text):
        # Placeholder; You'll need to implement this
        raise NotImplementedError

    def summarize_zine(self):
        conv = ClaudeConversation()
        conv.add_message(human_message=summarize_template, context=self.pdf_text)
        plan_template = get_zine_plan_template(
            len(self.layoutConfig.pages), self.style, self.content_type
        )
        conv.add_message(human_message=plan_template)
        conv.scrub_context()
        # self.zine_plan_conversation = conv.conversation
        self.zine_content.add_summary(conv.conversation)
        self._trigger_callback()
        return conv.conversation

    def plan_page(self, page_number, image_count=0, short_count=0, long_count=0):
        assert self.zine_plan_conversation is not None, "Must summarize zine first"
        conv = ClaudeConversation()
        conv.conversation = self.zine_content.summary
        page_template = get_page_template(
            page_number, image_count, short_count, long_count
        )
        page_plan_text = conv.add_message(human_message=page_template)
        self.zine_content.add_page_content(
            page_number, extract_page_reply(page_plan_text)
        )
        self._trigger_callback()
        return page_plan_text

    def plan_zine(self, parallel=False):
        self.summarize_zine()

        if parallel:
            num_pages = len(self.layoutConfig.pages)

            # Create a pool of worker processes based on the number of pages
            with multiprocessing.Pool(processes=num_pages) as pool:
                # Use starmap for functions with multiple arguments
                pool.starmap(
                    self.plan_page,
                    [
                        (i, page.image_count, page.short_count, page.long_count)
                        for i, page in enumerate(self.layoutConfig.pages)
                    ],
                )
        else:
            for i, page in enumerate(self.layoutConfig.pages):
                self.plan_page(i, page.image_count, page.short_count, page.long_count)

        return self.zine_content


if __name__ == "__main__":
    # Usage:
    def my_callback(zine_content):
        # Do something with the updated zine content
        print("Zine content updated!")

    planner = ZinePlanner(
        pdf_text="Input Research Paper Text Here",
        style="modern",
        callback=my_callback,
    )
    zine_data = planner.plan_zine()
