from setuptools import find_packages, setup

with open("README.md", "r") as fh:
   long_description = fh.read()

setup(
    name='terminalcast',
    version='1.0.0',
    description='Cast local videos to your chromecast',
    keywords=['Chromecast', 'video', 'local', 'movie'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/vanadinit/terminalcast',
    author='Johannes Paul',
    author_email='vanadinit@quantentunnel.de',
    license='MIT',
    python_requires='>=3.10',
    install_requires=[
        'bottle',
        'ffmpeg-python',
        'paste',
        'pychromecast>=13.0.0',
        'zeroconf==0.31.0',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'terminalcast=terminalcast:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
