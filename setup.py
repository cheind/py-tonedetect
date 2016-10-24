

from setuptools import setup

with open("tonedetect/version.py") as f: 
    exec(f.read())

setup(name='tonedetect',
      version=__version__,
      description='Capture tone sequences from real-time audio streams in Python',
      url='https://github.com/cheind/py-tonedetect',
      author='Christoph Heindl',
      author_email='christoph.heindl@gmail.com',
      license='BSD',
      packages=['tonedetect', 'tonedetect.bin'],
      include_package_data=True,
      zip_safe=False,
      setup_requires=['pytest-runner'],
      tests_require=['pytest']
      )
