#!/usr/bin/env python3
"""
Build script for FreeOverlay using PyInstaller.

Generates standalone executables for Windows and Linux.
Run: python scripts/build.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
PYTHON_DIR = PROJECT_ROOT / "python"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"

# Main entry point
MAIN_SCRIPT = PYTHON_DIR / "cyber_watch.py"

# Output names
APP_NAME = "FreeOverlay"
VERSION = "9.0.0"


def clean_build():
    """Remove previous build artifacts."""
    print("🧹 Cleaning previous builds...")
    for dir_path in [DIST_DIR, BUILD_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removed: {dir_path}")


def build_executable():
    """Build executable using PyInstaller."""
    print(f"\n🔨 Building {APP_NAME} {VERSION}...")

    # Determine OS
    is_windows = sys.platform == "win32"
    is_linux = sys.platform.startswith("linux")

    if not (is_windows or is_linux):
        print(f"❌ Unsupported platform: {sys.platform}")
        sys.exit(1)

    platform_name = "Windows" if is_windows else "Linux"
    print(f"   Platform: {platform_name}")

    # PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        # Basic options
        "--name",
        APP_NAME,
        "--windowed",  # No console window
        "--onefile",  # Single executable file
        # Version info
        "--version-file" if is_windows else "--add-data",
        *(["version_info.txt:."] if is_windows else []),
        # Icon
        "--icon" if is_windows else "",
        *(["icon.ico"] if is_windows and Path("icon.ico").exists() else []),
        # Python path
        "--paths",
        str(PYTHON_DIR),
        # Hidden imports (needed for dynamic loads)
        "--hidden-import=openvr",
        "--hidden-import=numpy",
        "--hidden-import=PIL",
        "--hidden-import=psutil",
        "--hidden-import=pyautogui",
        "--hidden-import=mss",
        "--hidden-import=OpenGL",
        "--hidden-import=glfw",
        "--hidden-import=winsdk" if is_windows else "",
        # Optimization
        "--optimize=2",
        "--strip" if is_linux else "",
        # Output directory
        "--distpath",
        str(DIST_DIR),
        "--buildpath",
        str(BUILD_DIR),
        # Main script
        str(MAIN_SCRIPT),
    ]

    # Remove empty strings from command
    cmd = [arg for arg in cmd if arg]

    print(f"\n   Command: {' '.join(cmd[:5])} ...")
    print()

    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with exit code {e.returncode}")
        return False


def create_package():
    """Create distributable packages."""
    print(f"\n📦 Creating distribution packages...")

    is_windows = sys.platform == "win32"
    platform_name = "Windows" if is_windows else "Linux"

    # Executable path
    exe_name = f"{APP_NAME}.exe" if is_windows else APP_NAME
    exe_path = DIST_DIR / exe_name

    if not exe_path.exists():
        print(f"❌ Executable not found: {exe_path}")
        return False

    # Create archive
    archive_name = f"{APP_NAME}-{VERSION}-{platform_name}"
    archive_path = DIST_DIR / archive_name

    print(f"   Creating: {archive_name}")

    try:
        if is_windows:
            # Windows: use zip
            output_path = shutil.make_archive(
                str(archive_path),
                "zip",
                DIST_DIR,
                exe_name,
            )
        else:
            # Linux: use tar.gz
            output_path = shutil.make_archive(
                str(archive_path),
                "gztar",
                DIST_DIR,
                exe_name,
            )

        print(f"   ✓ Created: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Failed to create archive: {e}")
        return False


def print_summary():
    """Print build summary."""
    print("\n" + "=" * 60)
    print("📊 BUILD SUMMARY")
    print("=" * 60)

    exe_name = f"{APP_NAME}.exe" if sys.platform == "win32" else APP_NAME
    exe_path = DIST_DIR / exe_name

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ Executable: {exe_path}")
        print(f"  Size: {size_mb:.1f} MB")

        # List other files in dist
        other_files = [f for f in DIST_DIR.iterdir() if f.is_file()]
        if other_files:
            print(f"\n✓ Additional files in dist/:")
            for file_path in other_files:
                size = file_path.stat().st_size / 1024
                print(f"  - {file_path.name} ({size:.1f} KB)")
    else:
        print("❌ Executable not found!")

    print("\n📁 Build directory structure:")
    print(f"  dist/     - Final executables and packages")
    print(f"  build/    - Build artifacts (temporary)")

    print("\n" + "=" * 60)


def main():
    """Main build workflow."""
    print("=" * 60)
    print(f"🚀 FreeOverlay Build Script v{VERSION}")
    print("=" * 60)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("\n❌ PyInstaller not installed!")
        print("   Install with: pip install pyinstaller")
        sys.exit(1)

    # Check if main script exists
    if not MAIN_SCRIPT.exists():
        print(f"\n❌ Main script not found: {MAIN_SCRIPT}")
        sys.exit(1)

    # Build workflow
    clean_build()
    success = build_executable()

    if success:
        create_package()
        print_summary()
    else:
        print("\n❌ Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
