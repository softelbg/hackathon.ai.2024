import gradio as gr

from sciveo.tools.logger import *
from evalidea.embedding import TextEmbedding


class GradioEvalIdeaView:
  def __init__(self, base_path, top_n, max_n):
    self.base_path = base_path
    self.top_n = top_n
    self.max_n = max_n

    self.interface = gr.Interface(
      fn=self.evaluate_idea,
      inputs=gr.Textbox(lines=4, placeholder="Enter your text here..."),
      outputs=gr.Textbox(),
      title="Evaluation of Ideas and Projects",
      description="Enter an idea to evaluate and click the button.",
      live=False
    )

  def evaluate_idea(self, input_text):
    embedder = TextEmbedding(base_path=self.base_path)
    embedder.load_db()
    result, result_prompt = embedder.search(input_text, self.top_n, self.max_n)
    debug("search", input_text, "found", len(result_prompt), len('\n'.join(result_prompt)))

    result = f"result: {result_prompt}"
    return result

  def launch(self):
    self.interface.launch()


if __name__ == "__main__":
  app = GradioEvalIdeaView()
  app.launch()
