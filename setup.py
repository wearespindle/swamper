from setuptools import find_packages, setup

import janitor


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    long_description = ''

install_requires = [
    'six>=1.10.0',
]

tests_require = [
    'pytest>=3.0.5',
    'pytest-cov>=2.4.0',
    'pytest-flake8>=0.8.1',
]

setup(
    name=janitor.__title__,
    version=janitor.__version__,
    description=('Janitor is a simple interface to clean input data and '
                 'turning this data into objects.'),
    long_description=long_description,
    url='https://github.com/wearespindle/janitor',
    author=janitor.__author__,
    author_email=janitor.__email__,
    license=janitor.__license__,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    keyword='janitor clean cleaning sanitation',
    classifiers=[
        # Status.
        'Development Status :: 3 - Alpha',

        # Audience.
        'Intended Audience :: Developers',

        # License.
        'License :: OSI Approved :: MIT License',

        # Programming languages.
        'Programming Language :: Python :: 2.7',
    ],
)
