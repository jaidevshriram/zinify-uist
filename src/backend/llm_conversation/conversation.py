from abc import ABC, abstractmethod
import re

class Conversation(ABC):
    def __init__(self, api_caller, message_template, context_template=None):
        self.api_caller = api_caller
        self.conversation = ""
        self.message_template = message_template
        self.context_template = context_template or ""
        self.context = ""  # in case there is no context
        self.messages = []


    def format_single_message(self, human_message, assistant_message):
        return self.message_template.format(
            human_message=human_message, assistant_message=assistant_message
        )

    def add_context(self, context):
        if self.context_template:
            self.context = self.context_template.format(context=context)
        else:
            self.context = context

    @abstractmethod
    def format_conversation(self, human_message, context=None):
        pass

    def add_message(self, human_message, context=None, retry=True, asst_message = ""):
        prompt, human_message = self.format_conversation(human_message, context, asst_message=asst_message)

        with open("prompt.txt", "w") as f:
            f.write(prompt)

        if retry:
            result = self.api_caller.call_with_retry(prompt)
        else:
            result = self.api_caller.call_api(prompt)

        result = asst_message + result

        with open("result.txt", "w") as f:
            f.write(result)

        if "Error" in str(result):
            print("API call failed.")
            return

        assistant_message = result.strip()
        self.conversation += self.format_single_message(
            human_message, assistant_message
        )

        self.messages.append(
            self.format_single_message(human_message, assistant_message)
        )

        return assistant_message

    def get_conversation(self):
        return self.conversation
    
    def undo_last_message(self):
        self.conversation = self.conversation[:-len(self.messages[-1])]

    def clear(self):
        self.conversation = ""
        self.messages = []
        self.context = ""
    
    def scrub_context(self):
        self.context = ""
        # use re to remove everything between <doc> and </doc>
        # re.sub('<doc>.+?</doc>', '', text, flags=re.DOTALL)
        self.conversation = re.sub('<doc>.+?</doc>', '', self.conversation, flags=re.DOTALL)
