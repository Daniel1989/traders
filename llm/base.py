class LlmClient:
    def __init__(self, model_name, is_chinese=True):
        self.model_name = model_name
        self.is_chinese = is_chinese

    def prompt(self, prompt_text, system_prompt=None):
        result = self.do_prompt(prompt_text, system_prompt)
        return result

    def do_prompt(self, prompt_text, system_prompt=None) -> str:
        raise Exception("Not implemented")
