from setuptools import setup, find_packages

setup(
    name="builderbot",
    version="0.1",
    packages=find_packages(),
    package_data={
        'builderbot': ['prompts/*.txt'],
    },
)
