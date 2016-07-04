from setuptools import setup

setup(name="gist",
      version="0.1",
      description="GIST is a simulation automation toolkit",
      url="https://github.com/shavvn/GIST.git",
      author="shavvn",
      author_email="tig314@gmail.com",
      packages=["gist"],
      install_requires=[
        "numpy",
        "matplotlib",
      ],
      classifiers=[
        "Development Status :: 0 dev release",
        "Programming Language :: Python :: 2.7",
        "Topic:: Automation"
      ],
      keywords="Research, Simulation, Data Visualization"
      )
