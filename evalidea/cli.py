import os
import argparse

from sciveo.tools.logger import *
from sciveo.tools.configuration import GlobalConfiguration
from sciveo.tools.remote import PredictorRemoteClient
from evalidea.reddit import RedditCrawler
from evalidea.embedding import TextEmbedding


def main():
  config = GlobalConfiguration.get(name='evalidea', reload=True)

  parser = argparse.ArgumentParser(description='Evaluate Idea CLI')
  parser.add_argument('command', choices=['init', 'crawl', 'embed', 'build', 'search'], help='Command to execute')
  parser.add_argument('--prompt', type=str, default="", help='prompt text')
  parser.add_argument('--limit', type=int, default=1, help='limit size')
  parser.add_argument('--path', type=str, default="./", help='path')
  parser.add_argument('--top-n', type=int, default=10, help='Top N')
  parser.add_argument('--max-n', type=float, default=3.0, help='Max N')
  args = parser.parse_args()

  if args.command == 'init':
    home = os.path.expanduser('~')
    base_path = os.path.join(home, '.evalidea')
    if not os.path.exists(base_path):
      os.makedirs(base_path)
      default_lines = [
        "REDDIT_USER=<user>",
        "REDDIT_CLIENT_ID=<client id>",
        "REDDIT_CLIENT_SECRET=<secret>",
        "log_min_level=DEBUG"
      ]
      with open(os.path.join(base_path, "default"), 'w') as fp:
        for line in default_lines:
          fp.write(line + '\n')
  elif args.command == 'crawl':
    debug("start crawling to", args.path)
    crawler = RedditCrawler(base_path=args.path)
    crawler.crawl_subreddit("shopify", limit=args.limit)
  elif args.command == 'embed':
    embedder = TextEmbedding(base_path=args.path)
    embedder.run()
  elif args.command == 'build':
    embedder = TextEmbedding(base_path=args.path)
    embedder.build_db()
  elif args.command == 'search':
    embedder = TextEmbedding(base_path=args.path)
    embedder.load_db()
    result, result_prompt = embedder.search(args.prompt, args.top_n, args.max_n)
    debug("search", args.prompt, "found", len(result_prompt))
    debug('\n'.join(result_prompt))
  else:
    warning(args.command, "not implemented")

if __name__ == '__main__':
  main()