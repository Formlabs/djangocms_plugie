#!/usr/bin/env python
from setuptools import find_packages, setup

from djangocms_plugie import __version__

with open('README.md') as f:
    long_description = f.read()

REQUIREMENTS = [
    'django-cms<3.7',
    'requests>=2.0',
]


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.8',
    'Framework :: Django',
    'Framework :: Django :: 1.11',
    'Framework :: Django CMS',
    'Framework :: Django CMS :: 3.6',
]


setup(
    name='djangocms-plugie',
    version=__version__,
    author='Alex Costa',
    author_email='alexandre.costa@code.berlin',
    maintainer='Formlabs Web Team',
    maintainer_email='web-software-team@formlabs.com',
    url='https://github.com/Formlabs/djangocms-plugie',
    license='MIT',
    description='Export/import django-cms plugins across applications.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'plugie=djangocms_plugie.setup_script:main',
        ],
    },
    package_data={
        'djangocms_plugie': [
            'templates/*.html',
            'static/*',
        ],
    },
    extras_require={
        "dev": [],
    },
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
)
