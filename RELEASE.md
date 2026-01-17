# FreeOverlay Release Guide

## Automated Release Process

FreeOverlay uses GitHub Actions to automatically build executables for Windows and Linux when you create a new release.

### Creating a Release

#### Method 1: Using Git Tags (Recommended)

```bash
# 1. Make sure all changes are committed
git status

# 2. Create a tag with version number
git tag -a v9.0.0 -m "Release version 9.0.0"

# 3. Push tag to GitHub
git push origin v9.0.0
```

#### Method 2: Using GitHub Web Interface

1. Go to your repository on GitHub
2. Click "Releases" in the sidebar
3. Click "Create a new release"
4. Create a new tag (e.g., `v9.0.0`)
5. Give it a title and description
6. Click "Publish release"

### What Happens Automatically

When you push a tag matching `v*`:

1. **GitHub Actions Workflow Triggers**
   - Build job for Windows
   - Build job for Linux

2. **For Each Platform**
   - Sets up Python environment
   - Installs dependencies from `requirements.txt`
   - Runs `scripts/build.py` to compile with PyInstaller
   - Creates distributable packages (`.zip` for Windows, `.tar.gz` for Linux)
   - Uploads artifacts to GitHub Actions

3. **Release Assets**
   - Both platform executables are automatically uploaded to the GitHub Release
   - Users can download from the Releases page

### Manual Build (Local Development)

#### Prerequisites

```bash
# Install Python 3.8+
python --version

# Install dependencies
pip install -r python/requirements.txt
```

#### Building Locally

```bash
# From project root
python scripts/build.py
```

Output:
```
dist/
├── FreeOverlay.exe          (Windows)
├── FreeOverlay              (Linux)
├── FreeOverlay-Windows-9.0.0.zip
└── FreeOverlay-Linux-9.0.0.tar.gz
```

### Build Script Details

The build script (`scripts/build.py`):

- ✅ Detects your OS automatically
- ✅ Cleans previous builds
- ✅ Compiles with PyInstaller
- ✅ Creates standalone executables
- ✅ Generates distributable packages
- ✅ Shows build summary

### Troubleshooting

#### "PyInstaller not found"
```bash
pip install pyinstaller
```

#### Build fails on Linux
```bash
# May need additional system packages
sudo apt-get install python3-dev
```

#### Build fails on Windows
```bash
# Use PowerShell as Administrator
# Or use conda environment
```

### Release Structure

```
Releases/
├── v9.0.0/
│   ├── FreeOverlay-Windows-9.0.0.zip
│   ├── FreeOverlay-Linux-9.0.0.tar.gz
│   └── Release notes
├── v9.0.1/
│   └── ...
```

### User Installation

**Windows:**
```bash
# Extract FreeOverlay-Windows-9.0.0.zip
# Run FreeOverlay.exe
```

**Linux:**
```bash
# Extract FreeOverlay-Linux-9.0.0.tar.gz
tar xzf FreeOverlay-Linux-9.0.0.tar.gz
# Run ./FreeOverlay
```

### Version Management

The version is defined in:
- `setup.py` → version field
- GitHub tag → v{version}
- CI/CD → automatically extracts from tag

To bump version:

```bash
# Update version in setup.py
vim setup.py
# Change: version="9.0.1"

# Commit and tag
git add setup.py
git commit -m "chore: bump version to 9.0.1"
git tag -a v9.0.1 -m "Release 9.0.1"
git push origin v9.0.1
```

### CI/CD Workflow File

See `.github/workflows/build.yml` for:
- Full build configuration
- Platform-specific steps
- Artifact upload settings
- Release creation logic

### Monitoring Builds

1. Go to GitHub repository
2. Click "Actions" tab
3. Watch build progress in real-time
4. Check logs if build fails

### Release Notes

Generate from commit history:
```bash
# See what changed since last tag
git log v9.0.0..HEAD --oneline
```

GitHub Actions can auto-generate these using `generate_release_notes: true`.

### Security Considerations

- Executable is built in CI/CD (no malicious code)
- All source code on GitHub is visible
- Checksums available from GitHub Release page
- Users can verify authenticity

### Future Enhancements

- [ ] Code signing for executables
- [ ] CHANGELOG.md auto-generation
- [ ] GitHub Release auto-drafts
- [ ] Multi-platform testing in CI
- [ ] Performance benchmarks
- [ ] Changelog integration with commits

---

**Questions?** Check the GitHub Actions logs or open an issue.
