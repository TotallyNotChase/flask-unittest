from setuptools import setup

with open('README.md', 'r') as readmefile:
    readme = readmefile.read()

setup(
    name='flask-unittest',
    version='0.1.3',
    url='https://github.com/TotallyNotChase/flask-unittest',
    license='MIT',
    author='TotallyNotChase',
    author_email='totallynotchase42@gmail.com',
    description='Unit testing flask applications made easy!',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=['flask_unittest'],
    test_suite="tests.normalsuite",
    platforms='any',
    install_requires=['Flask>=1.1.0'],
    tests_require=['selenium', 'beautifulsoup4'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.6',
)
