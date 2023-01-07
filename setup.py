from distutils.core import setup
from setuptools import find_packages
import os


# User-friendly description from README.md
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''

setup(
    # Name of the package
    name="Hybrid-SC-Algorithm",

    # Packages to include into the distribution
    packages=find_packages('.',include=['supply_chain_network']), 

    # Start with a small number and increase it with every change you make
    # https://semver.org
    version='0.0.1',

    # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    # For example: MIT
    license='MIT',

    # Short description of your library
    description='a package that implement the hybrid-supply-chain algorithm',

    # Long description of your library
    long_description = long_description,
    long_description_context_type = 'text/markdown',

    # Your name
    author='Maged S. Al-Shaibani', 

    # Your email
    author_email='mageedsaeed1@gmail.com',     

    # Either the link to your github or to your website
    url='https://github.com/MagedSaeed/Hybrid-SC-Algorithm',

    # Link from which the project can be downloaded
    download_url='git+https://github.com/MagedSaeed/Hybrid-SC-Algorithm',

    # List of keyword arguments
    keywords=[],

    # List of packages to install with this one
    install_requires=[open(f'{current_directory}/requirements.txt').read().splitlines()],

    # https://pypi.org/classifiers/
    classifiers=[]  
)