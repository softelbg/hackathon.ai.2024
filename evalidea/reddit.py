import os
import time
import json
import praw

from sciveo.tools.logger import *
from sciveo.tools.configuration import GlobalConfiguration


class RedditCrawler:
  def __init__(self, base_path="./"):
    self.config = GlobalConfiguration.get()

    client_id = self.config["REDDIT_CLIENT_ID"]
    client_secret = self.config["REDDIT_CLIENT_SECRET"]
    user_agent = f"Reddit API client by u/{self.config['REDDIT_USER']}"

    self.reddit = praw.Reddit(client_id=client_id,
                              client_secret=client_secret,
                              user_agent=user_agent)
    self.base_path = base_path
    self.path_data_file = os.path.join(base_path, "data.json")
    self.path_meta_file = os.path.join(base_path, "meta.json")

    self.meta_data = {"after": ""}

    if os.path.isfile(self.path_data_file):
      with open(self.path_data_file, 'r') as file:
        self.data = json.load(file)
    else:
      self.data = {}
    debug("user_agent", user_agent, "path_data_file", self.path_data_file, "current size", len(self.data))

  def crawl_subreddit(self, subreddit_name, limit=100):
    subreddit = self.reddit.subreddit(subreddit_name)

    if os.path.isfile(self.path_meta_file):
      with open(self.path_meta_file, 'r') as fp:
        self.meta_data = json.load(fp)

    for submission in subreddit.hot(limit=limit, params={'after': self.meta_data["after"]}):
      try:
        self.save_submission(submission)
        debug(f"saved submission: {submission.title}")
      except Exception as e:
        error("exception", e)
      time.sleep(1)

  def save_submission(self, submission):
    self.data.setdefault(submission.id, {})
    self.data[submission.id] = {
      "title": submission.title,
      "fullname": submission.fullname,
      "content": submission.selftext,
      "url": submission.url,
      "comments": []
    }

    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
      try:
        self.data[submission.id]["comments"].append({"author": comment.author.name, "body": comment.body})
      except Exception as e:
        error("exception", e)

    with open(self.path_data_file, 'w') as fp:
      json.dump(self.data, fp, indent=2)

    with open(self.path_meta_file, 'w') as fp:
      json.dump({"after": submission.fullname}, fp, indent=2)

if __name__ == "__main__":
  crawler = RedditCrawler()
  crawler.crawl_subreddit("shopify", limit=1)
