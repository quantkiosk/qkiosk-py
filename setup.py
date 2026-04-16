from setuptools import setup, find_packages

setup(
  #install_requires=['requests', 'numpy', 'pandas'], #external packages as dependencies
  packages=find_packages(),
  package_data={'qkiosk': ['datasets/*']}
)
