from setuptools import setup, find_packages

with open('README.md', 'r') as readmefile:
    readme = readmefile.read()

setup(
    name='flask-unittest',
    version='0.0.1',
    url='https://github.com/TotallyNotChase/flask-unittest',
    license='MIT',
    author='TotallyNotChase',
    author_email='totallynotchase42@gmail.com',
    description='Unit test flask applications with unittest!',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    test_suite="tests.suite",
    platforms='any',
    install_requires=['Flask>=1.1.0'],
    tests_require=['selenium'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.6',
)
