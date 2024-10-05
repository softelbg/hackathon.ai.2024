import os
from openai import OpenAI

class Openai:
    def __init__(self):
      api_key = os.environ.get('OPENAI_API_KEY')
      self.client = OpenAI(api_key=api_key)

    def promt(self, context, current_prompt, max_tokens=300):
      combined_prompt = f"{context}\n{current_prompt}"

      PROMPT_MESSAGES = [
                          {
                            "role": "user",
                            "content": combined_prompt
                          }
                      ]

      params = {
                "model": "gpt-4",
                "messages": PROMPT_MESSAGES,
                "max_tokens": max_tokens,
              }

      return self.client.chat.completions.create(**params).choices[0].message.content

if __name__ == "__main__":
	gpt = Openai()
	context = "This conversation is about evaluating startup ideas."
	current_prompt = "Is teleport a good startup idea?"
	result = gpt.promt(context, current_prompt, 300)
	print(result)
