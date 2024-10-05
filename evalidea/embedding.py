import os
import json

from annoy import AnnoyIndex

from sciveo.tools.logger import *
from sciveo.tools.configuration import GlobalConfiguration
from sciveo.tools.remote import PredictorRemoteClient


class TextEmbedding:
  def __init__(self, base_path="./"):
    self.base_path = base_path
    self.path_data_file = os.path.join(base_path, "data.json")
    self.path_embed_file = os.path.join(base_path, "embeddings.json")
    self.path_map_file = os.path.join(base_path, "map.json")
    self.path_db_file = os.path.join(base_path, "annoy.db")

    self.client = PredictorRemoteClient(url="https://sof-1.softel.bg:8901", verify=False)

    if os.path.isfile(self.path_data_file):
      with open(self.path_data_file, 'r') as fp:
        debug("load", self.path_data_file)
        self.data = json.load(fp)
    else:
      self.data = {}

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

  def build_db(self):
    with open(self.path_embed_file, 'r') as fp:
      debug("load", self.path_embed_file)
      self.embeddings = json.load(fp)

    self.map = {}
    self.vdb = AnnoyIndex(768, 'euclidean')

    info("Building vector db on", len(self.embeddings ), "submissions")
    idx = 0
    for id, submission in self.embeddings.items():
      for k in ["title", "content"]:
        self.vdb.add_item(idx, submission[k])
        self.map[idx] = {"id": id, "column": k}
        idx += 1
      for i, c in enumerate(submission["comments"]):
        self.vdb.add_item(idx, c)
        self.map[idx] = {"id": id, "column": "comments", "pos": i}
        idx += 1

    debug("db size", idx)

    self.vdb.build(200)
    self.vdb.save(self.path_db_file)
    with open(self.path_map_file, 'w') as fp:
      json.dump(self.map, fp, indent=2)

  def load_db(self):
    self.vdb = AnnoyIndex(768, 'euclidean')
    self.map = {}

    if os.path.exists(self.path_db_file):
      debug("load", self.path_db_file)
      self.vdb.load(self.path_db_file)

      with open(self.path_map_file, 'r') as fp:
        debug("load", self.path_map_file)
        self.map = json.load(fp)

  def search(self, text):
    embedding = self.embed_one(text)
    idx, d = self.vdb.get_nns_by_vector(embedding, 3, search_k=-1, include_distances=True)
    debug("search", text, "=>", idx, "distance", d)
    result = []
    for i, id in enumerate(idx):
      id = str(id)
      submission = self.data[self.map[id]["id"]]
      text = submission[self.map[id]["column"]]
      if "pos" in self.map[id]:
        text = text[self.map[id]["pos"]]
      result.append({"submission": submission, "text": text, "dist": d[i]})
    return result


if __name__ == "__main__":
  config = GlobalConfiguration.get(name='evalidea', reload=True)
  embedder = TextEmbedding()
  embedder.run()
