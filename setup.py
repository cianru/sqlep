from setuptools import setup, find_packages

setup(
    name='sqlep',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/cianru/sqlep',
    license='Apache 2.0',
    author='cian dream team',
    author_email='etl@cian.ru',
    description='a tool for testing sql queries',
    install_requires=[
        'pandas==0.*',
        'PyHive[hive]>=0.6.1',
        'pytest>=4.0',
        'pytest-mock>=1.1.0',
    ]
)
