from setuptools import setup, find_packages
import re

with open('imitation_chess/__init__.py') as f:
    versionString = re.search(r"__version__ = '(.+)'", f.read()).group(1)

if __name__ == '__main__':
    setup(name='imitation_chess',
        version = versionString,
        author="Reid McIlroy-Young",
        packages = find_packages(),
        install_requires = [
                'numpy',
                'matplotlib',
                'pandas',
                'seaborn',
                'python-chess'
        ]
    )
