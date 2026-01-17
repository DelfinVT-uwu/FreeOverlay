"""
FreeOverlay Setup Configuration

Defines package metadata, dependencies, and entry points.
Supports installation and distribution.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="FreeOverlay",
    version="9.0.0",
    author="Dolphin Engineering",
    author_email="",
    description="OpenGL-based VR Overlay with system monitoring, calendar, media control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/madkoding/FreeOverlay",
    project_urls={
        "Bug Tracker": "https://github.com/madkoding/FreeOverlay/issues",
        "Source Code": "https://github.com/madkoding/FreeOverlay",
    },
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    python_requires=">=3.8",
    install_requires=[
        "openvr>=1.23",
        "numpy>=1.21",
        "Pillow>=9.0",
        "psutil>=5.8",
        "pyautogui>=0.9.53",
        "mss>=6.2",
        "PyOpenGL>=3.1",
        "glfw>=2.1",
        # Windows-specific
        "winsdk>=1.0; sys_platform == 'win32'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "sphinx>=4.5",
        ],
        "build": [
            "pyinstaller>=5.0",
            "build>=0.8",
            "wheel>=0.37",
        ],
    },
    entry_points={
        "console_scripts": [
            "freeoverlay=python.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Graphics :: Viewers",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    keywords="vr overlay monitoring calendar media",
    include_package_data=True,
    zip_safe=False,
)
