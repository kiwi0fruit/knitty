from setuptools import setup, find_packages
from os import path

import versioneer


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pandoctools',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

    description='Another CLI for Stitch/Knotr: reproducible report generation tool via Jupyter, Pandoc and Markdown.',
    long_description=long_description,

    url='https://github.com/kiwi0fruit/knitty',

    author='Peter Zagubisalo',
    author_email='peter.zagubisalo@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    # keywords='sample setuptools development',
    packages=find_packages(exclude=['docs', 'tests']),

    install_requires=['jupyter_core', 'traitlets', 'ipython', 'jupyter_client',
                      'nbconvert', 'pandocfilters', 'pypandoc', 'click', 'psutil'],

    include_package_data=True,
    package_data={
        'knitty': ['stitch/*.py', 'stitch/static/*'],
    },
    entry_points={
        'console_scripts': [
            'knitty=knitty.knitty:main',
            'pre-knitty=knitty.pre_knitty:main',
        ],
    },
)
