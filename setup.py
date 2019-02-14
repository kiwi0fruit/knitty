from setuptools import setup, find_packages
from os import path
import io
import versioneer


here = path.abspath(path.dirname(__file__))

with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='knitty',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

    description='Inrterface wrapper for Stitch/Knotr: reproducible report generation tool via Jupyter, Pandoc and Markdown. Export to Jupyter notebook via Notedown.',
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/kiwi0fruit/knitty',

    author='Peter Zagubisalo',
    author_email='peter.zagubisalo@gmail.com',

    license='GPLv2+',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='atom hydrogen jupyter pandoc markdown report',
    packages=find_packages(exclude=['docs', 'tests']),

    install_requires=['jupyter_core', 'traitlets', 'ipython', 'jupyter_client',
                      'nbconvert', 'pandocfilters', 'py-pandoc', 
                      'click', 'psutil', 'panflute>=1.11.2',
                      'nbformat', 'pandoc-attrs', 'pyyaml'],
    python_requires='>=3.6',
    extras_require={
        'dev': ['pytest', 'pytest-cov', 'sphinx', 'pandas', 'matplotlib', 'sphinx_rtd_theme', 'ghp-import',  # for stitch
                'nose'],  # for notedown; more conda packages: 'r-knitr', 'r-reticulate'
    },
    # conda install -c defaults -c conda-forge pytest pytest-cov sphinx pandas matplotlib sphinx_rtd_theme ghp-import nose r-knitr r-reticulate

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
