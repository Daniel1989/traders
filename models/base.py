class LlmClient:
    def __init__(self, model_name):
        self.model_name = model_name

    def prompt(self, prompt_text, system_prompt=None):
        result = self.do_prompt(prompt_text, system_prompt)
        return result

    def do_prompt(self, prompt_text, system_prompt=None):
        raise Exception("Not implemented")