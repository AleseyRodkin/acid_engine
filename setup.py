from setuptools import setup, find_packages

setup(
    name='acid_engine',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    extras_require={'test': ['pytest']},
    author='Твое Имя',
    description='Contract-oriented data engine',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)   