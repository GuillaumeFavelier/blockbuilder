import io
import os
import os.path as op
from setuptools import setup

NAME = 'blockbuilder'
AUTHOR = 'Guillaume Favelier'
AUTHOR_EMAIL = 'guillaume.favelier@gmail.com'
DESCRIPTION = 'Block building application'
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = 'http://github.com/GuillaumeFavelier/blockbuilder'
CLASSIFIERS = [
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Operating System :: MacOS :: MacOS X',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'Topic :: Artistic Software',
    'Topic :: Software Development',
]

REQUIREMENTS = None
with open('requirements.txt') as f:
    REQUIREMENTS = [line.rstrip('\n') for line in f]

# Adapted from MNE
VERSION = None
with open(op.join(NAME, '__init__.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            VERSION = line.split('=')[1].strip().strip('\'')
            break


# Adapted from VisPy
def package_tree(pkgroot):
    """Get the submodule list."""
    path = op.dirname(__file__)
    subdirs = [op.relpath(i[0], path).replace(op.sep, '.')
               for i in os.walk(op.join(path, pkgroot))
               if '__init__.py' in i[2]]
    return sorted(subdirs)


# Adapted from Spyder
with io.open('README.md', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()
SCRIPTS = ['blockbuilder']
if os.name == 'nt':
    SCRIPTS += ['blockbuilder.bat']


setup_args = dict(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    license=LICENSE,
    download_url=DOWNLOAD_URL,
    url=DOWNLOAD_URL,
    platforms=["Windows", "Linux", "MacOS"],
    python_requires='>=3.7',
    install_requires=REQUIREMENTS,
    packages=package_tree(NAME),
    scripts=[op.join('scripts', fname) for fname in SCRIPTS],
    classifiers=CLASSIFIERS,
)

setup(**setup_args)
