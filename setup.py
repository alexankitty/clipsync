from setuptools import setup

setup(
    name='clipsync',
    version='1.0.0',
    description='The daemon that lives in your computer that shuttles wayland and xorg clipboards',
    license='GPL-2.0',
    packages=['clipsync'],
    author='Alexandra Stone',
    author_email='alexankitty@gmail.com',
    keywords=['clipboard', 'synchronization', 'wayland', 'xorg', 'x11'],
    url='https://github.com/alexankitty/clipsync',
    entry_points={
        'console_scripts': [
            'clipsync = clipsync.clipsync:main',
        ]
    }
)