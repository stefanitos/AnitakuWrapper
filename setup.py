from setuptools import setup, find_packages

setup(
    name='AnitakuWrapper',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'beautifulsoup4',
        'lxml',
    ],
)