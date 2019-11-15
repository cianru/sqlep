from setuptools import setup, find_packages

setup(
    name='sqlep',
    version='0.0.1',
    packages=find_packages(),
    url='github.com/cian-github/sqlep',
    license='Apache 2.0',
    author='cian dream team',
    author_email='ml@cian.ru',
    description='a tool for testing sql queries',
    install_requires=[
        'pandas==0.21.1',
        'PyHive[hive]==0.6.1',
        'pytest==5.2.2',
        'pytest-mock==1.11.2',
    ]
)
