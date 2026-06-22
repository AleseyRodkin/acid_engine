from setuptools import setup, find_packages

setup(
    name='acid-engine',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['pandas', 'pyyaml', 'simpleeval'],
    author='Alexey Rodkin',
    description='Contract-oriented data control layer',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AleseyRodkin/acid_engine',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
    ],
)