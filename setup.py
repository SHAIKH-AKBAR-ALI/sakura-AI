from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Anime_AI",
    version="0.0.1",
    packages=find_packages(),
    author="shaikh akbar ali",
    install_requires=requirements,
)