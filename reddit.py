import os
import praw

from sciveo.tools.logger import *


class RedditCrawler:
  def __init__(self, client_id, client_secret, user_agent, dst_folder):
    self.reddit = praw.Reddit(client_id=client_id,
                              client_secret=client_secret,
                              user_agent=user_agent)
    self.dst_folder = dst_folder

    if not os.path.exists(self.dst_folder):
      os.makedirs(self.dst_folder)
    debug(user_agent, "->", dst_folder)

  def crawl_subreddit(self, subreddit_name, limit=100):
    subreddit = self.reddit.subreddit(subreddit_name)

    for submission in subreddit.hot(limit=limit):
      self.save_submission(submission)
      debug(f"saved submission: {submission.title}")

  def save_submission(self, submission):
    """Save the submission (post) and its comments to text files."""
    submission_folder = os.path.join(self.dst_folder, f"{submission.id}_{submission.title[:50]}")
    if not os.path.exists(submission_folder):
      os.makedirs(submission_folder)

    submission_file = os.path.join(submission_folder, "post.txt")
    with open(submission_file, 'w', encoding='utf-8') as f:
      f.write(f"Title: {submission.title}\n\n")
      f.write(f"Content: {submission.selftext}\n")
      f.write(f"URL: {submission.url}\n")

    submission.comments.replace_more(limit=None)
    comments_file = os.path.join(submission_folder, "comments.txt")
    with open(comments_file, 'w', encoding='utf-8') as f:
      for comment in submission.comments.list():
        f.write(f"Comment by {comment.author}: {comment.body}\n")
        f.write("-" * 80 + "\n")


if __name__ == "__main__":
  client_id = os.environ["REDDIT_CLIENT_ID"]
  client_secret = os.environ["REDDIT_CLIENT_SECRET"]
  user_agent = f"Reddit API client by u/{os.environ['REDDIT_USER']}"

  crawler = RedditCrawler(client_id, client_secret, user_agent, dst_folder="reddit_data")
  crawler.crawl_subreddit("shopify", limit=1)
