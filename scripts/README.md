# Build Scripts

Scripts for building FreeOverlay executables on different platforms.

## Quick Start

### Windows
```bash
scripts\build.bat
```

### Linux / macOS
```bash
./scripts/build.sh
```

### Cross-Platform (Python)
```bash
python scripts/build.py
```

## What These Scripts Do

1. **Check Prerequisites**
   - Python 3.8+
   - PyInstaller

2. **Install Dependencies**
   - From `python/requirements.txt`

3. **Compile Application**
   - Bundles Python + all dependencies
   - Creates standalone executable
   - Optimizes for size and performance

4. **Create Distributions**
   - Windows: `.zip` archive
   - Linux: `.tar.gz` archive

## Output

```
dist/
├── FreeOverlay.exe              (Windows executable)
├── FreeOverlay                  (Linux executable)
├── FreeOverlay-Windows-*.zip    (Distributable)
└── FreeOverlay-Linux-*.tar.gz   (Distributable)
```

## Platform-Specific Scripts

### build.bat (Windows)
- Batch script for Windows Command Prompt
- Automatically checks for Python in PATH
- Shows helpful error messages
- Colored output

Usage:
```batch
cd \path\to\FreeOverlay
scripts\build.bat
```

### build.sh (Linux/macOS)
- Bash script for Unix-like systems
- Requires Python 3 installed
- Shows build progress with colors

Usage:
```bash
cd /path/to/FreeOverlay
./scripts/build.sh
```

### build.py (Cross-Platform)
- Pure Python, works everywhere
- Detects OS automatically
- Most flexible for CI/CD

Usage:
```bash
python scripts/build.py
```

## Requirements

### Windows
- Python 3.8+ (from python.org)
- Visual C++ Build Tools (usually auto-installed by pip)

### Linux
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip

# Fedora/RHEL
sudo dnf install python3-devel python3-pip

# Arch
sudo pacman -S python
```

### macOS
```bash
# Using Homebrew
brew install python3

# Or use system Python 3
```

## Troubleshooting

### "Python not found"
- **Windows**: Add Python to PATH during installation
- **Linux/macOS**: Install Python 3, then use `python3` instead of `python`

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### Build fails with cryptic errors
1. Check that `python/` directory exists
2. Verify `cyber_watch.py` is the main script
3. Check `requirements.txt` for valid packages
4. Try: `pip install --upgrade pyinstaller`

### Permission denied on Linux
```bash
chmod +x scripts/build.sh
```

## GitHub Actions CI/CD

These scripts are automatically run by GitHub Actions (`.github/workflows/build.yml`):
- On every tag push (e.g., `git tag v9.0.0`)
- Builds for Windows and Linux in parallel
- Uploads executables to GitHub Releases
- Generates archive files

For manual testing, see `.github/workflows/build.yml`.

## Advanced Usage

### Custom Output Directory
```bash
# In build.py, modify DIST_DIR
DIST_DIR = Path(__file__).parent.parent / "my_custom_dist"
```

### Different Entry Point
```bash
# In build.py, change MAIN_SCRIPT
MAIN_SCRIPT = PYTHON_DIR / "my_main.py"
```

### With Console Window (Windows)
```python
# In build.py, remove: "--windowed"
```

### Icon Support
```bash
# Place icon.ico in project root
# Uncomment icon handling in build.py
```

## Performance Optimization

The build scripts already include:
- ✅ `--onefile` (single executable)
- ✅ `--optimize=2` (Python optimization level)
- ✅ `--strip` on Linux (remove debug symbols)
- ✅ Only bundle required dependencies

## File Size

Typical executable sizes:
- **Windows**: 80-150 MB
- **Linux**: 60-120 MB

Includes:
- Full Python runtime
- NumPy, PIL, OpenVR
- PyOpenGL and dependencies

## Contributing

To modify the build process:

1. Update `scripts/build.py` for core logic
2. Update `scripts/build.bat` for Windows specifics
3. Update `scripts/build.sh` for Linux specifics
4. Test on both platforms

## Questions?

- See `RELEASE.md` for release process
- Check `.github/workflows/build.yml` for CI/CD configuration
- Open an issue on GitHub
