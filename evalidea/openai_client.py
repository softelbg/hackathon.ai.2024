import os
import json
import requests
from openai import OpenAI

from sciveo.tools.logger import *
from sciveo.tools.configuration import GlobalConfiguration


class OpenaiIdeaEval:
  def __init__(self):
    self.config = GlobalConfiguration.get()
    self.api_key = self.config['OPENAI_API_KEY']
    self.client = OpenAI(api_key=self.api_key)

  def preprocess(self, data):
    result = ''
    for chunk in data:
      result += chunk['submission']['title'] + ' ' + chunk['submission']['content'] + ' '
    return result

  def __call__(self, data, current_prompt):
    current_prompt = f"Is {current_prompt} a good startup idea? Give me short answer of the score from 1 to 10, for example: score: 3 / 10"
    context = self.preprocess(data)
    combined_prompt = f"Context:\n{context}\n\nQuestion:\n{current_prompt}"
    # combined_prompt = combined_prompt.encode('ascii', 'ignore').decode('ascii')

    params = {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "user",
          "content": combined_prompt
        }
      ],
      "max_tokens": 128
    }

    # return self.client.chat.completions.create(**params).choices[0].message.content

    headers = {
      "Content-Type": "application/json; charset=UTF-8",
      "Authorization": f"Bearer {self.api_key}"
    }

    response = requests.post(
      'https://api.openai.com/v1/chat/completions',
      headers=headers,
      json=params
    )

    if response.status_code == 200:
      return response.json()["choices"][0]["message"]["content"]
    else:
      raise Exception(f"OpenAI API request failed: {response.text}")


if __name__ == "__main__":
  config = GlobalConfiguration.get(name='evalidea', reload=True)

  current_prompt = "shopify plugin development for sales forecast, predictions and reporting analytics"
  current_prompt = "shopify plugin development for visual search, using uploaded image of item"

  from evalidea.embedding import TextEmbedding
  embedder = TextEmbedding()
  embedder.load_db()
  result, result_prompt = embedder.search(current_prompt, top_n=10, max_distance=2.8)
  answer = OpenaiIdeaEval()(result, current_prompt)
  debug(answer)
