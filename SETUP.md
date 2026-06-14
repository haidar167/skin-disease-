# 🎓 Skin Disease Detection System - Setup Guide

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Local Installation

#### Step 1: Clone the Repository
```bash
git clone https://github.com/haidar167/skin-disease-.git
cd skin-disease-
```

#### Step 2: Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Run the Application
```bash
python university_skin_system.py
```

---

## Docker Installation

### Using Docker

#### Build Docker Image
```bash
docker build -t skin-disease-detection:latest .
```

#### Run Docker Container
```bash
docker run -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/skin_disease.db:/app/skin_disease.db \
  --name skin-disease-app \
  skin-disease-detection:latest
```

### Using Docker Compose

#### Start Services
```bash
docker-compose up -d
```

#### View Logs
```bash
docker-compose logs -f skin-disease-app
```

#### Stop Services
```bash
docker-compose down
```

---

## GitHub Actions CI/CD

### Automated Workflows Included

1. **Python CI/CD Pipeline** (`python-ci.yml`)
   - Tests on Python 3.8, 3.9, 3.10, 3.11
   - Syntax validation
   - Dependency checks
   - Automated on push and pull requests

2. **Docker Build** (`docker-build.yml`)
   - Builds Docker images
   - Validates Dockerfile
   - Tests containerization

3. **Code Analysis & Security** (`code-analysis.yml`)
   - Code quality checks
   - Security scanning with Bandit
   - Dependency vulnerability checks

### Viewing Workflow Results

1. Go to **Actions** tab on GitHub
2. Select a workflow
3. View job details and logs
4. Check the build summary for status

---

## System Requirements

### Minimum
- OS: Windows 7+, macOS 10.12+, or Linux
- CPU: 2 GHz processor
- RAM: 2 GB
- Disk: 500 MB

### Recommended
- OS: Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- CPU: Intel Core i5 or equivalent
- RAM: 4 GB or more
- Disk: 1 GB SSD

---

## Python Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| torch | Latest | Deep learning framework |
| torchvision | Latest | Computer vision tools |
| Pillow | Latest | Image processing |
| numpy | Latest | Numerical computing |
| scikit-learn | Latest | Machine learning tools |
| tqdm | Latest | Progress bars |
| matplotlib | Latest | Data visualization |

---

## Troubleshooting

### Issue: ImportError for tkinter
**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk@3.10

# Windows
# Reinstall Python with tkinter option selected
```

### Issue: Database locked error
**Solution:**
```bash
# Close all instances of the application
# Delete skin_disease.db (it will recreate automatically)
rm skin_disease.db
```

### Issue: GPU/CUDA errors with PyTorch
**Solution:**
```bash
# Install CPU-only version of PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Issue: Port already in use
**Solution:**
```bash
# Change port in code or use different container
docker run -p 5001:5000 skin-disease-detection:latest
```

---

## Testing

### Run Syntax Check
```bash
python -m py_compile university_skin_system.py
```

### Verify Installation
```bash
python -c "import sqlite3, tkinter; print('✓ Installation verified')"
```

### Test Database
```bash
python -c "
import sqlite3
conn = sqlite3.connect('skin_disease.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM diseases')
print(f'✓ Database contains {cursor.fetchone()[0]} diseases')
"
```

---

## Demo Credentials

| Field | Value |
|-------|-------|
| Email | demo@patient.com |
| Password | demo123 |

---

## Development

### Running Tests with GitHub Actions
Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Weekly schedule (Sundays)

### View Results
1. Go to **Actions** tab
2. Select **Python CI/CD Pipeline**
3. View detailed logs

---

## Support

For issues or questions:
1. Check **Issues** tab on GitHub
2. Create a new issue with detailed description
3. Include logs and error messages

---

## License

This project is for educational use. See LICENSE file for details.

---

## Version History

- **v2.0** - Enhanced UI, disease management, report export
- **v1.0** - Initial release

Last Updated: 2024
