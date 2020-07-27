from distutils.core import setup

setup(
  name = 'hdfwriter',         # How you named your package folder (MyLib)
  packages = ['hdfwriter'],   # Chose the same as "name"
  version = '0.1.4',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Stream data to an HDF5 File',   # Give a short description about your library
  author = 'James Gao, Helene Moorman, Suraj Gowda',                   # Type in your name
  url = 'https://github.com/sgowda/hdfwriter',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/sgowda/hdfwriter/archive/v0.1.2.tar.gz',    # I explain this later on
  keywords = ['HDF5', 'Data Serialization'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'h5py',
          'tables',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 2.7',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
