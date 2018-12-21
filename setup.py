from setuptools import setup, find_packages
from os import path

import versioneer


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='knitty',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

    description='Inrterface wrapper for Stitch/Knotr: reproducible report generation tool via Jupyter, Pandoc and Markdown. Export to Jupyter notebook via Notedown.',
    long_description=long_description,

    url='https://github.com/kiwi0fruit/knitty',

    author='Peter Zagubisalo',
    author_email='peter.zagubisalo@gmail.com',

    license='MIT (knitty, stitch), BSD 2-Clause (notedown)',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='atom hydrogen jupyter pandoc markdown report',
    packages=find_packages(exclude=['docs', 'tests']),

    install_requires=['jupyter_core', 'traitlets', 'ipython', 'jupyter_client',
                      'nbconvert', 'pandocfilters', 'pypandoc',
                      'click', 'psutil', 'panflute',
                      'nbformat', 'pandoc-attributes', 'six', 'pyyaml'],
    # install_requires=['knotr>0.4.1', 'click', 'psutil', 'panflute', 'notedown>1.5.1'],

    extras_require={
        'dev': ['pytest', 'pytest-cov', 'sphinx', 'pandas', 'matplotlib', 'sphinx_rtd_theme', 'numpydoc'],
    },

    include_package_data=True,
    package_data={
        'knitty': ['stitch/*', 'stitch/static/*', 'notedown/*', 'notedown/templates/*'],
    },
    entry_points={
        'console_scripts': [
            'knitty=knitty.knitty:main',
            'pre-knitty=knitty.pre_knitty:main',
            'knotr=knitty.stitch.cli:cli',
            'knotedown = knitty.notedown.main:app',
        ],
    },
)
