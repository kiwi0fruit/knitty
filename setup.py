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

    description="Reproducible report generation tool via Jupyter, Pandoc and Markdown.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/kiwi0fruit/knitty',

    author='Peter Zagubisalo',
    author_email='peter.zagubisalo@gmail.com',

    license='MIT License',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='atom hydrogen jupyter pandoc markdown report',
    packages=find_packages(exclude=['docs', 'tests']),

    install_requires=['jupyter_core', 'traitlets', 'ipython', 'jupyter_client', 'ipykernel',
                      'nbconvert>=5.4.1', 'pandocfilters', 'py-pandoc>=2.6',
                      'click', 'psutil', 'panflute>=1.11.2', 'shutilwhich-cwdpatch>=0.1.0',
                      'pyyaml'],
    # jupyter_core traitlets ipython jupyter_client nbconvert pandocfilters "py-pandoc>=2.6" click psutil "panflute>=1.11.2" pyyaml "shutilwhich-cwdpatch>=0.1.0" ipykernel
    python_requires='>=3.6',
    extras_require={
        'dev': ['pytest', 'pytest-cov', 'pandas', 'matplotlib', 'sphinx', 'sphinx_rtd_theme', 'ghp-import'],
    },
    # test: pytest pytest-cov pandas matplotlib
    # docs: sphinx sphinx_rtd_theme ghp-import

    include_package_data=True,
    entry_points={
        'console_scripts': [
            'knitty=knitty.knitty:main',
            'pre-knitty=knitty.pre_knitty:main',
            'pandoc-filter-arg=knitty.pandoc_filter_arg.cli:cli',
        ],
    },
)
