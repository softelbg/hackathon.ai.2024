import gradio as gr

from sciveo.tools.logger import *
from evalidea.embedding import TextEmbedding
from evalidea.openai_client import OpenaiIdeaEval


class GradioEvalIdeaView:
  def __init__(self, base_path, top_n, max_n):
    self.base_path = base_path
    self.top_n = top_n
    self.max_n = max_n

    with gr.Blocks() as self.interface:
      gr.Markdown("# Startup Idea Evaluation")
      gr.Markdown("Enter a startup idea and click the button to evaluate.")

      with gr.Row():
        with gr.Column():
          self.input_text = gr.Textbox(lines=4, placeholder="Enter your text here...")
          self.submit_button = gr.Button("Evaluate")
          self.image_output = gr.Image("/Users/sgeorgiev/Downloads/IMG_3024.JPG", label="Image Output", height=600)

        with gr.Column():
          self.output_text = gr.Textbox(label="Score")
          self.debug_output = gr.Textbox(label="Debug Output")

      self.submit_button.click(self.evaluate_idea, inputs=self.input_text, outputs=[self.output_text, self.debug_output])

  def evaluate_idea(self, input_text):
    embedder = TextEmbedding(base_path=self.base_path)
    embedder.load_db()
    result, result_prompt = embedder.search(input_text, self.top_n, self.max_n)
    debug("search", input_text, "found", len(result_prompt), len('\n'.join(result_prompt)))
    score = OpenaiIdeaEval()(result, input_text)
    debug_text = result
    return score, debug_text

  def launch(self):
    self.interface.launch()


if __name__ == "__main__":
  config = GlobalConfiguration.get(name='evalidea', reload=True)

  app = GradioEvalIdeaView(base_path="./", top_n=10, max_n=2.8)
  app.launch()
