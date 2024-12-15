from setuptools import setup, find_packages

setup(
    name="stagereminder",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)