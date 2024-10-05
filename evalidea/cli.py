import os
import argparse

from sciveo.tools.logger import *
from sciveo.tools.configuration import GlobalConfiguration


def main():
  config = GlobalConfiguration.get()

  parser = argparse.ArgumentParser(description='Evaluate Idea CLI')
  parser.add_argument('command', choices=['init'], help='Command to execute')
  parser.add_argument('--path-dst', type=str, default="./data", help='dst path')
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

