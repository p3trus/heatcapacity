from setuptools import setup, find_packages

requires = ['future']

desc = ('A lightweight python package to simplify the communication with '
        'several scientific instruments.')

setup(
    name='heatcapacity',
    version=__import__('heatcapacity').__version__,
    author='Marco Halder',
    author_email='marco.halder@frm2.tum.de',
    license = 'BSD',
    url='https://github.com/p3trus/heatcapacity',
    description=desc,
    long_description=open('README.md').read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
)
