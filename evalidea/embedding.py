import os
import json

from sciveo.tools.logger import *
from sciveo.tools.configuration import GlobalConfiguration
from sciveo.tools.remote import PredictorRemoteClient


class TextEmbedding:
  def __init__(self, base_path="./"):
    self.base_path = base_path
    self.path_data_file = os.path.join(base_path, "data.json")
    self.path_embed_file = os.path.join(base_path, "embeddings.json")
    self.path_map_file = os.path.join(base_path, "map.json")

    if os.path.isfile(self.path_data_file):
      with open(self.path_data_file, 'r') as fp:
        debug("load", self.path_data_file)
        self.data = json.load(fp)
    else:
      self.data = {}

    self.client = PredictorRemoteClient(url="https://sof-1.softel.bg:8901", verify=False)

  def embed_one(self, text):
    max_size = 1024
    if len(text) > max_size:
      warning("big size", len(text))
    X = [
      text[:max_size].encode('ascii', 'ignore').decode('ascii').replace('`', '').replace('\n', ' ')
    ]

    params = {
      "predictor": "TextEmbedding",
      "compressed": True,
      "X": X,
    }

    r = self.client.predict(params)
    Y = r[params["predictor"]]
    debug("stats", r["stats"], len(Y[0]))
    return Y[0]

  def run(self):
    if os.path.isfile(self.path_embed_file):
      with open(self.path_embed_file, 'r') as fp:
        debug("load", self.path_embed_file)
        self.embeddings = json.load(fp)
    else:
      self.embeddings = {}

    for i, (id, submission) in enumerate(self.data.items()):
      if id in self.embeddings:
        debug("SKIP", i, id)
        continue

      debug(i, id, submission)
      self.embeddings[id] = {}

      for k in ["title", "content"]:
        self.embeddings[id][k] = self.embed_one(submission[k])

      self.embeddings[id]["comments"] = []
      for c in submission["comments"]:
        self.embeddings[id]["comments"].append(self.embed_one(c["body"]))

      if i % 1 == 0:
        with open(self.path_embed_file, 'w') as fp:
          json.dump(self.embeddings, fp, indent=2)


if __name__ == "__main__":
  config = GlobalConfiguration.get(name='evalidea', reload=True)
  embedder = TextEmbedding()
  embedder.run()
