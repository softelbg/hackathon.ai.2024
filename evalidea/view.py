import gradio as gr
import json

from sciveo.tools.logger import *
from evalidea.embedding import TextEmbedding
from evalidea.openai_client import OpenaiIdeaEval


class GradioEvalIdeaView:
  def __init__(self, base_path, top_n, max_n, share=False):
    self.base_path = base_path
    self.top_n = top_n
    self.max_n = max_n
    self.share = share

    with gr.Blocks() as self.interface:
      gr.Markdown("# Startup Idea Evaluation")
      gr.Markdown("Enter a startup idea and click the button to evaluate.<br>Currently only shopify-related ideas (mostly for shopify plugins) are evaluated.")

      with gr.Row():
        with gr.Column():
          self.input_text = gr.Textbox(lines=4, placeholder="Enter your text here...")
          self.submit_button = gr.Button("Evaluate")
          self.output_text = gr.Markdown(value="[GIThub hackathon.ai.2024](https://github.com/softelbg/hackathon.ai.2024)")
          # self.image_output = gr.Image("/Users/sgeorgiev/Downloads/IMG_3024.JPG", label="Image Output", height=600)

        with gr.Column():
          self.output_score = gr.Markdown(label="score", value="")
          self.output_text = gr.Textbox(label="Score")
          self.output_found = gr.Markdown(label="data found", value="")
          self.debug_output = gr.Textbox(label="Debug Output")

      self.submit_button.click(self.evaluate_idea, inputs=self.input_text, outputs=[self.output_score, self.output_text, self.output_found, self.debug_output])

  def evaluate_idea(self, input_text):
    embedder = TextEmbedding(base_path=self.base_path)
    embedder.load_db()
    result, result_submissions = embedder.search(input_text, self.top_n, self.max_n)
    debug("search found", len(result), len(result_submissions), input_text)

    score = OpenaiIdeaEval(result).score(input_text)

    score_text = score
    try:
      score = json.loads(score.replace("```json\n", "").replace("\n```", "").strip())
      score_text = f"score: {score['score']} / 10\n\nexplain: {score['explain']}"
    except:
      warning("can not parse", score)

    debug_text = ""
    html = ""
    html_score = ""

    try:
      debug_text += f"score: {score['score']}\n"
      if score['score'] < 5:
        html_score = f"<br><p class='center-text' style='color: red;font-size: 20px;'>HOLD</p>"
      elif score['score'] > 5:
        html_score = f"<br><p class='center-text' style='color: green;font-size: 20px;'>BUY</p>"
      else:
        html_score = f"<br><p class='center-text' style='color: orange;'>HM...</p>"
    except:
      warning("can not parse", score)

    html += "<br>"

    debug_text += f"{len(result_submissions)} signals found\n"
    for s in result_submissions:
      debug_text += f"{s['submission']['title']} D[{s['dist']:.2f}] [link]({s['submission']['url']})\n"
      if 'body' in s['text']:
        text = s['text']['body'].replace('\n', ' ')
        debug_text += f" --- comment: [{text[:80]}]\n"
    debug_text += "\n"
    html += debug_text.replace("\n", "<br>")

    return html_score, score_text, html, debug_text

  def launch(self):
    self.interface.launch(share=self.share)


if __name__ == "__main__":
  config = GlobalConfiguration.get(name='evalidea', reload=True)

  app = GradioEvalIdeaView(base_path="./", top_n=10, max_n=2.8)
  app.launch(share=False)
