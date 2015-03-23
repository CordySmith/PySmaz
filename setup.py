from setuptools import setup


setup(
    name='pySmaz',
    version='1.0.1',
    packages=['smaz', 'tests'],
    url='https://github.com/cordysmith/PySmaz/',
    license='BSD',
    description='A small string compression library written in pure python.',
    author='Max Smith',
    author_email='',
    test_suite='tests.test_smaz',
)
