from setuptools import setup

setup(
    name='sqlep',
    version='0.0.1',
    packages=['sqlep'],
    url='github.com/cian-github/sqlep',
    license='Apache 2.0',
    author='cian dream team',
    author_email='ml@cian.ru',
    description='a tool for testing sql queries',
    install_requires=[
        'pandas==0.21.1',
        'pytest==5.2.2',
        'pytest-mock==1.11.2',
    ]
)
