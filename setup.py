from setuptools import setup, find_packages

extras_require = {
  "all": []
}

setup(
    name='evalidea',
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
      'numpy>=0.0.0',
      'requests>=0.0.0',
      'sciveo[media]>=0.0.0',
      'praw>=0.0.0',
      'annoy>=0.0.0',
      'openai>=0.0.0',
      'flask>=0.0.0',
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    extras_require=extras_require,
    py_modules=['evalidea'],
    entry_points={
      'console_scripts': [
        'evalidea=evalidea.cli:main',
      ],
    },
)
