from setuptools import setup, find_packages

setup(
    name='acid-engine',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'pyyaml',
        'simpleeval',
        'lark-parser'
    ],
    extras_require={
        'dev': ['pytest', 'build', 'twine']
    },
    entry_points={
        'console_scripts': [
            'acid = acid_engine.cli.main:main',
        ],
    },
    author='Alexey Rodkin',
    author_email='aleksejrodkin5@gmail.com',
    description='Contract-Driven Data Control Layer',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AleseyRodkin/acid_engine',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)