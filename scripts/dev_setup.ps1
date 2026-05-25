# Create venv and install backend requirements
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r ..\backend\requirements.txt
