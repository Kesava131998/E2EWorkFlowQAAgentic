# Joulez · E2E Workflow Dashboard — Windows PowerShell starter
# Equivalent of start.sh
# Run with: powershell -ExecutionPolicy Bypass -File start.ps1

$ErrorActionPreference = "Stop"

$ROOT       = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SERVER_DIR = Join-Path $ROOT "server"
$CLIENT_DIR = Join-Path $ROOT "client"

# --- Colours (ANSI — works in Windows Terminal / PowerShell 7+)
$CYAN   = "`e[0;36m"
$GREEN  = "`e[0;32m"
$YELLOW = "`e[1;33m"
$NC     = "`e[0m"

# --- Resolve Python: prefer conda/miniconda Python over system Python 3.14
# System Python 3.14 breaks pydantic-core (pyo3 max supported = 3.13)
$CONDA_PY_PATHS = @(
    "$env:USERPROFILE\miniconda3\python.exe",
    "$env:USERPROFILE\anaconda3\python.exe",
    "C:\ProgramData\miniconda3\python.exe",
    "C:\ProgramData\anaconda3\python.exe",
    "C:\miniconda3\python.exe",
    "C:\anaconda3\python.exe"
)

$PY = $null
foreach ($candidate in $CONDA_PY_PATHS) {
    if (Test-Path $candidate) {
        $PY = $candidate
        break
    }
}

if (-not $PY) {
    # Fall back to whatever python3 / python is in PATH
    $PY = (Get-Command python -ErrorAction SilentlyContinue)?.Source
    if (-not $PY) {
        Write-Error "Python not found. Install Miniconda/Anaconda or add Python to PATH."
        exit 1
    }
}

$PY_VER = & "$PY" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"

Write-Host "${CYAN}"
Write-Host "  ╔══════════════════════════════════════╗"
Write-Host "  ║   Joulez · E2E Workflow Dashboard    ║"
Write-Host "  ╚══════════════════════════════════════╝"
Write-Host "${NC}"
Write-Host "  Using Python $PY_VER at $PY"
Write-Host ""

# --- [1/3] Python deps
Write-Host "${YELLOW}[1/3] Installing server dependencies...${NC}"
& "$PY" -m pip install -q -r (Join-Path $SERVER_DIR "requirements.txt")

# --- [2/3] Node deps
Write-Host "${YELLOW}[2/3] Installing client dependencies...${NC}"
Set-Location $CLIENT_DIR
npm install --silent

# --- [3/3] Start both
Write-Host "${YELLOW}[3/3] Starting dashboard...${NC}"
Write-Host ""
Write-Host "  ${GREEN}API server${NC}  → http://localhost:8765"
Write-Host "  ${GREEN}Dashboard${NC}   → http://localhost:5173  (opens automatically)"
Write-Host ""
Write-Host "  Then run your workflow:    ${CYAN}/e2e-workflow JP-1${NC}"
Write-Host "  Or run the self-heal demo: ${CYAN}/self-heal-demo${NC}"
Write-Host ""

# --- Ensure ports are free before starting
foreach ($port in @(8765, 5173)) {
    $pids = (netstat -ano | Select-String ":$port\s" | ForEach-Object {
        ($_ -split '\s+')[-1]
    } | Sort-Object -Unique)
    foreach ($p in $pids) {
        if ($p -match '^\d+$' -and $p -ne '0') {
            try { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue } catch {}
        }
    }
}

# --- Start FastAPI server in background
$serverJob = Start-Job -ScriptBlock {
    param($py, $dir)
    & "$py" "$dir\main.py"
} -ArgumentList $PY, $SERVER_DIR

Write-Host "  Server PID (Job): $($serverJob.Id)"

# Give server a moment to start
Start-Sleep -Seconds 1

# --- Start Vite in foreground (Ctrl-C stops it)
Set-Location $CLIENT_DIR
try {
    npm run dev
} finally {
    # Cleanup on exit — kill background server job
    Write-Host ""
    Write-Host "${YELLOW}Shutting down API server...${NC}"
    Stop-Job  -Job $serverJob -ErrorAction SilentlyContinue
    Remove-Job -Job $serverJob -ErrorAction SilentlyContinue
    Write-Host "${GREEN}Done.${NC}"
}
