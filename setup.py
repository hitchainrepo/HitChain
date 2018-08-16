from setuptools import setup

setup(
    name = 'hit',
    version = '0.1.0',
    packages = ['hit'],
    entry_points = {
        'console_scripts': [
            'hit = hit.__main__:main'
        ]
    })
