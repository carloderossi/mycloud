# uv Quick Reference - MyCloud Authentication

## 🚀 One-Command Setup

### Linux/macOS
```bash
bash setup.sh
```

### Windows
```powershell
.\setup.ps1
```

---

## 📦 Manual Setup (Step by Step)

### 1. Install uv

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

### 2. Create Virtual Environment

```bash
uv venv
```

This creates a `.venv` directory.

---

### 3. Activate Virtual Environment

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

---

### 4. Install Dependencies

```bash
uv pip install -r requirements.txt
```

---

### 5. Create .env File

```bash
cp .env.example .env
```

Then edit `.env` with your credentials.

---

### 6. Run the Script

```bash
python mycloud_simple.py
```

---

## 🔧 Common uv Commands

```bash
# Install a package
uv pip install package-name

# Install with specific version
uv pip install package-name==1.2.3

# Install from requirements.txt
uv pip install -r requirements.txt

# Upgrade a package
uv pip install --upgrade package-name

# Uninstall a package
uv pip uninstall package-name

# List installed packages
uv pip list

# Show package details
uv pip show package-name

# Freeze current packages
uv pip freeze > requirements.txt

# Check for updates
uv pip list --outdated
```

---

## 📝 Project Workflow

```bash
# 1. Initial setup
uv venv
source .venv/bin/activate  # or Windows equivalent
uv pip install -r requirements.txt
cp .env.example .env

# 2. Edit .env with credentials
nano .env

# 3. Run the script
python mycloud_simple.py

# 4. Deactivate when done
deactivate
```

---

## 🔄 Daily Workflow

```bash
# Activate environment
source .venv/bin/activate  # Linux/Mac
# or
.\.venv\Scripts\Activate.ps1  # Windows

# Run your script
python mycloud_simple.py

# Deactivate when done
deactivate
```

---

## 🧹 Cleanup

```bash
# Remove virtual environment
rm -rf .venv

# Remove cached packages (optional)
rm -rf ~/.cache/uv
```

---

## 🆘 Troubleshooting

### uv not found after installation
```bash
# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Make permanent (Linux/Mac)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Virtual environment not activating
```bash
# Check if .venv exists
ls -la .venv

# Recreate if needed
rm -rf .venv
uv venv
```

### Package installation fails
```bash
# Try with verbose output
uv pip install -v -r requirements.txt

# Try installing packages one by one
uv pip install python-dotenv
uv pip install selenium
uv pip install selenium-wire
uv pip install requests
uv pip install webdriver-manager
```

### Permission denied
```bash
# Make script executable (Linux/Mac)
chmod +x setup.sh

# Run with sudo if needed
sudo uv pip install -r requirements.txt
```

---

## 📊 Quick Comparison

| Task | pip | uv |
|------|-----|-----|
| Install package | `pip install pkg` | `uv pip install pkg` |
| From requirements | `pip install -r req.txt` | `uv pip install -r req.txt` |
| Create venv | `python -m venv .venv` | `uv venv` |
| Speed | ⏱️ Baseline | ⚡ 10-100x faster |

---

## ✅ Verification Checklist

After setup, verify:

- [ ] uv is installed: `uv --version`
- [ ] Virtual environment exists: `ls .venv`
- [ ] Environment is activated: `which python` (should show .venv)
- [ ] Packages installed: `uv pip list`
- [ ] .env file created with credentials
- [ ] Script runs: `python mycloud_simple.py`

---

## 🎯 Most Common Commands

```bash
# Complete setup (from scratch)
uv venv && source .venv/bin/activate && uv pip install -r requirements.txt

# Daily use
source .venv/bin/activate && python mycloud_simple.py

# Update all packages
uv pip install --upgrade -r requirements.txt

# Clean and reinstall
rm -rf .venv && uv venv && source .venv/bin/activate && uv pip install -r requirements.txt
```

---

## 💡 Pro Tips

1. **Always activate venv before running scripts**
2. **Use `uv pip list` to verify installations**
3. **Keep requirements.txt updated**
4. **Never commit .env or .venv to git**
5. **Use `.gitignore` to exclude sensitive files**

---

## 📚 Resources

- **uv GitHub:** https://github.com/astral-sh/uv
- **uv Docs:** https://github.com/astral-sh/uv/blob/main/README.md
- **Python venv:** https://docs.python.org/3/library/venv.html
