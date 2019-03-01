from setuptools import setup

setup(name='cmsh',
      version='0.1',
      description="High level interface over Mate Soos's pycryptosat from CryptoMiniSat",
      url='http://github.com/cipherboy/cmsh',
      author='Alexander Scheel',
      author_email='alexander.m.scheel@gmail.com',
      license='GPLv2',
      packages=['cmsh'],
      install_requires=['pycryptosat'],
      zip_safe=True)
