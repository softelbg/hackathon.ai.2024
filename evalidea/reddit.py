import os
import time
import json
import praw

from sciveo.tools.logger import *
from sciveo.tools.configuration import GlobalConfiguration


class RedditCrawler:
  def __init__(self, path_data):
    self.config = GlobalConfiguration.get()

    client_id = self.config["REDDIT_CLIENT_ID"]
    client_secret = self.config["REDDIT_CLIENT_SECRET"]
    user_agent = f"Reddit API client by u/{self.config['REDDIT_USER']}"

    self.reddit = praw.Reddit(client_id=client_id,
                              client_secret=client_secret,
                              user_agent=user_agent)
    self.path_data = path_data

    if os.path.isfile(path_data):
      with open(path_data, 'r') as file:
        self.data = json.load(file)
    else:
      self.data = {}
    debug("user_agent", user_agent, "path_data", path_data, "current size", len(self.data))

  def crawl_subreddit(self, subreddit_name, limit=100):
    subreddit = self.reddit.subreddit(subreddit_name)

    for submission in subreddit.hot(limit=limit):
      self.save_submission(submission)
      debug(f"saved submission: {submission.title}")
      time.sleep(1)

  def save_submission(self, submission):
    self.data.setdefault(submission.id, {})
    self.data[submission.id] = {
      "title": submission.title,
      "content": submission.selftext,
      "url": submission.url,
      "comments": []
    }

    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
      self.data[submission.id]["comments"].append({"author": comment.author.name, "body": comment.body})

    with open(self.path_data, 'w') as fp:
      json.dump(self.data, fp, indent=2)

if __name__ == "__main__":
  crawler = RedditCrawler(path_data="./data.json")
  crawler.crawl_subreddit("shopify", limit=1)
