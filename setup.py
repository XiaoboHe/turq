import os

from setuptools import setup

metadata = {}
with open(os.path.join('turq', '__metadata__.py'), 'r') as f:
    exec(f.read(), metadata)            # pylint: disable=exec-used

with open('README.rst') as f:
    long_description = f.read()


setup(
    name='turq',
    version=metadata['version'],
    description='Mock HTTP server',
    long_description=long_description,
    url='https://github.com/vfaronov/turq',
    author='Vasiliy Faronov',
    author_email='vfaronov@gmail.com',
    license='ISC',
    packages=['turq'],
    package_data={'turq': ['editor/*', 'examples.rst']},
    entry_points={'console_scripts': ['turq=turq.main:main']},
    install_requires=[
        'h11 >= 0.7.0',
        'falcon >= 1.1.0',
        'dominate >= 2.3.1',
        'Werkzeug >= 0.12.1',
        'docutils >= 0.13.1',
        'coloredlogs >= 6.0',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
    keywords='HTTP Web server mock mocking test debug',
)
