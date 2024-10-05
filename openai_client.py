import os
import json
from openai import OpenAI

class Openai:
    def __init__(self):
      api_key = os.environ.get('OPENAI_API_KEY')
      self.client = OpenAI(api_key=api_key)

    def preprocess(self, data):
      result = ''
      for chunk in data:
        result += chunk['submission']['title'] + ' ' + chunk['submission']['content'] + ' '
      return result

    def __call__(self, data, current_prompt, max_tokens=300):
      context = self.preprocess(data)
      # context = ''
      # context = self.gpt.promt(context, current_prompt, 300)
      combined_prompt = f"{context}\n{current_prompt}"

      PROMPT_MESSAGES = [
                          {
                            "role": "user",
                            "content": combined_prompt
                          }
                      ]

      params = {
                "model": "gpt-4o",
                "messages": PROMPT_MESSAGES,
                "max_tokens": max_tokens,
              }

      return self.client.chat.completions.create(**params).choices[0].message.content

if __name__ == "__main__":
  with open('/Users/ivanivanov/tmp/R1-1.json', 'r') as file:
    data = json.load(file)
  current_prompt = "Is shopify plugin development for sales forecast, predictions and reporting analytics, is a good startup idea?, give me short answer - from 1 to 10, and long answer with explanation"
  answer = Openai()(data, current_prompt)
  print(answer)
