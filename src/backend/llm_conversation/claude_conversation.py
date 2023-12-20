from .conversation import Conversation
from ..llm_api_wrappers import ClaudeApiCaller

message_template = "\n\nHuman:{human_message}\n\nAssistant:{assistant_message}"

context_template = """<doc>
{context}
</doc>"""


class ClaudeConversation(Conversation):
    def __init__(self):
        super().__init__(ClaudeApiCaller(), message_template, context_template)

    def format_conversation(self, human_message, context=None, asst_message = ""):
        if context:
            self.add_context(context)
            human_message = self.context + "\n" + human_message
        prompt = self.conversation + self.format_single_message(human_message, asst_message)
        return prompt, human_message
