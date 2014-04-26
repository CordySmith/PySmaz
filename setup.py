from distutils.core import setup

setup(
    name='pySmaz',
    version='1.0.0',
    packages=['lib', 'tests'],
    url='https://github.com/cordysmith/PySmaz/',
    license='BSD',
    author='Max Smith',
    author_email='',
    description='A small string compression library written in pure python.',
    test_suite='tests.test_smaz'
)
