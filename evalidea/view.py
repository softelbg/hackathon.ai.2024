import gradio as gr

from sciveo.tools.logger import *
from evalidea.embedding import TextEmbedding


class GradioEvalIdeaView:
  def __init__(self, base_path, top_n, max_n):
    self.base_path = base_path
    self.top_n = top_n
    self.max_n = max_n

    with gr.Blocks() as self.interface:
      gr.Markdown("# Idea Evaluation")
      gr.Markdown("Enter an idea and click the button to evaluate.")

      with gr.Row():
        with gr.Column():
          self.input_text = gr.Textbox(lines=4, placeholder="Enter your text here...")
          self.submit_button = gr.Button("Evaluate")
          self.image_output = gr.Image("/Users/sgeorgiev/Downloads/sky_gate_cert.jpg", label="Image Output", height=300)

        with gr.Column():
          self.output_text = gr.Textbox(label="Output")
          self.debug_output = gr.Textbox(label="Debug Output")

      self.submit_button.click(self.evaluate_idea, inputs=self.input_text, outputs=[self.output_text, self.debug_output])

  def evaluate_idea(self, input_text):
    embedder = TextEmbedding(base_path=self.base_path)
    embedder.load_db()
    result, result_prompt = embedder.search(input_text, self.top_n, self.max_n)
    debug("search", input_text, "found", len(result_prompt), len('\n'.join(result_prompt)))

    result_prompt = f"result: {result_prompt}"
    debug_text = result
    return result_prompt, debug_text

  def launch(self):
    self.interface.launch()


if __name__ == "__main__":
  app = GradioEvalIdeaView()
  app.launch()
