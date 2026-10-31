$ErrorActionPreference='Stop'
$start=Get-Date
python --version; git --version
python -m venv .venv; .\.venv\Scripts\pip install -r requirements-dev.txt
"bootstrap_seconds=$([int]((Get-Date)-$start).TotalSeconds)"
