# from distutils.core import setup
from setuptools import setup
import twps

with open('README.rst', 'r') as f:
    long_description = f.read()
    long_description_type = 'text/x-rst'

setup(name='twps',
      packages=['twps', ],

      # Use setuptools_scn
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      license='GPL',

      description='TWPS: (T)ext (W)ith (P)ython (S)nippets preprocessor',
      long_description=long_description,
      long_description_content_type=long_description_type,
      author='A.Travleev',
      author_email='anton.travleev@gmail.com',
      url='https://github.com/inr-kit/twps',
      keywords='TEXT PYTHON SNIPPETS TEMPLATE PREPROCESSOR'.split(),
      scripts=['twps/ppp.py'],
      package_data={
          '': ['*.rst'],  # for readme.rst
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 2.7',
          'Topic :: Text Processing :: Markup',
          'Topic :: Text Processing :: Filters',
          'Topic :: Text Processing :: General',
          'Topic :: Utilities',
      ],
      )
