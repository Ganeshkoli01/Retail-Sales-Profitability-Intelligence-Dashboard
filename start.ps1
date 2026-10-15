<#
.SYNOPSIS
    Interactive PowerShell Startup & Orchestration Script for Retail Sales & Profitability Analytics.

.DESCRIPTION
    Provides automated environment validation, virtual environment activation,
    and a streamlined menu / CLI flags to run the pipeline, test suite, Streamlit dashboard,
    open the Excel workbook, or launch the Jupyter notebook.

.PARAMETER RunPipeline
    Runs the full end-to-end data pipeline (ingestion, cleaning, SQLite loading, Excel export, charts).

.PARAMETER RunTests
    Executes the automated pytest test suite (17 tests).

.PARAMETER Dashboard
    Launches the interactive Streamlit web application.

.PARAMETER OpenExcel
    Opens the generated 10-sheet corporate Excel workbook in the default spreadsheet app.

.PARAMETER Notebook
    Launches the exploratory analysis Jupyter notebook.

.EXAMPLE
    .\start.ps1
    Launches the interactive console menu.

.EXAMPLE
    .\start.ps1 -RunPipeline
    Executes the analytics pipeline directly.

.EXAMPLE
    .\start.ps1 -Dashboard
    Starts the Streamlit web dashboard.
#>

[CmdletBinding()]
param(
    [switch]$RunPipeline,
    [switch]$RunTests,
    [switch]$Dashboard,
    [switch]$OpenExcel,
    [switch]$Notebook
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

# Colors & Formatting
function Write-Header {
    param([string]$Text)
    Write-Host "`n==================================================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "==================================================================" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Text)
    Write-Host "[SUCCESS] $Text" -ForegroundColor Green
}

function Write-Info {
    param([string]$Text)
    Write-Host "[INFO] $Text" -ForegroundColor Yellow
}

function Write-Alert {
    param([string]$Text)
    Write-Host "[ALERT] $Text" -ForegroundColor Red
}

# 1. Environment Verification
function Check-PythonEnvironment {
    Write-Info "Verifying Python environment..."
    
    # Check if virtual environment exists
    $VenvActivate = Join-Path $ScriptDir ".venv\Scripts\Activate.ps1"
    if (Test-Path $VenvActivate) {
        Write-Info "Activating local virtual environment (.venv)..."
        & $VenvActivate
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $PyVer = python --version 2>&1
        Write-Success "Using System Python: $PyVer"
    } else {
        Write-Alert "Python was not found in your system PATH! Please install Python 3.10+ from python.org."
        exit 1
    }
}

# 2. Workflow Actions
function Invoke-Pipeline {
    Write-Header "RUNNING FULL RETAIL ANALYTICS PIPELINE"
    python -m src.main
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Pipeline completed successfully!"
    } else {
        Write-Alert "Pipeline encountered errors. Please inspect the log output above."
    }
}

function Invoke-TestSuite {
    Write-Header "EXECUTING AUTOMATED PYTEST SUITE"
    pytest -v
    if ($LASTEXITCODE -eq 0) {
        Write-Success "All tests passed with 100% success rate!"
    } else {
        Write-Alert "Some tests failed. Check test logs above."
    }
}

function Invoke-Dashboard {
    Write-Header "LAUNCHING STREAMLIT INTERACTIVE DASHBOARD"
    Write-Info "Starting web server at http://localhost:8501 (Press Ctrl+C to stop)..."
    streamlit run app/streamlit_app.py
}

function Invoke-OpenExcel {
    $ExcelPath = Join-Path $ScriptDir "excel\retail_sales_analytics.xlsx"
    if (Test-Path $ExcelPath) {
        Write-Info "Opening Excel Workbook: $ExcelPath"
        Invoke-Item $ExcelPath
        Write-Success "Workbook opened in default spreadsheet viewer."
    } else {
        Write-Alert "Excel workbook not found! Running pipeline first to generate it..."
        Invoke-Pipeline
        Invoke-Item $ExcelPath
    }
}

function Invoke-Notebook {
    Write-Header "LAUNCHING JUPYTER EXPLORATORY NOTEBOOK"
    $NbPath = Join-Path $ScriptDir "notebooks\exploratory_analysis.ipynb"
    if (Get-Command jupyter -ErrorAction SilentlyContinue) {
        jupyter notebook $NbPath
    } else {
        Write-Info "Starting notebook via Python module..."
        python -m notebook $NbPath
    }
}

# 3. Interactive Menu
function Show-InteractiveMenu {
    Clear-Host
    Write-Host @"
==================================================================
   RETAIL SALES & PROFITABILITY ANALYTICS - CONTROL CONSOLE
   Placement Portfolio Project | Python, SQLite, Excel, Streamlit
==================================================================
"@ -ForegroundColor Cyan

    Write-Host "Select an analytical action to perform:`n" -ForegroundColor White
    Write-Host "  [1] Run Full Analytics Pipeline (ETL, SQLite, Visuals, Excel)" -ForegroundColor Yellow
    Write-Host "  [2] Launch Interactive Streamlit Web Dashboard" -ForegroundColor Yellow
    Write-Host "  [3] Run Automated Test Suite (17 pytest tests)" -ForegroundColor Yellow
    Write-Host "  [4] Open 10-Sheet Corporate Excel Workbook" -ForegroundColor Yellow
    Write-Host "  [5] Launch Exploratory Jupyter Notebook" -ForegroundColor Yellow
    Write-Host "  [6] Open SQLite Database CLI (`retail_analytics.db`)" -ForegroundColor Yellow
    Write-Host "  [7] View Data Quality & Business Findings Reports" -ForegroundColor Yellow
    Write-Host "  [0] Exit`n" -ForegroundColor DarkGray

    $Choice = Read-Host "Enter your choice [0-7]"
    switch ($Choice) {
        "1" { Invoke-Pipeline }
        "2" { Invoke-Dashboard }
        "3" { Invoke-TestSuite }
        "4" { Invoke-OpenExcel }
        "5" { Invoke-Notebook }
        "6" { 
            Write-Info "Opening SQLite database..."
            if (Get-Command sqlite3 -ErrorAction SilentlyContinue) {
                sqlite3 database\retail_analytics.db
            } else {
                python -c "import sqlite3; conn = sqlite3.connect('database/retail_analytics.db'); print('Tables:', [r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")]); conn.close()"
                Write-Info "Tip: Install sqlite3 CLI to interactively query from terminal."
            }
        }
        "7" {
            Write-Header "ANALYTICAL REPORTS DIRECTORY"
            Get-ChildItem "reports" | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
            Write-Info "Reports are in markdown format in the 'reports/' folder."
        }
        "0" { 
            Write-Info "Exiting console. Goodbye!"
            return
        }
        Default {
            Write-Alert "Invalid option selected."
        }
    }
}

# Main Execution Routing
Check-PythonEnvironment

if ($RunPipeline) {
    Invoke-Pipeline
} elseif ($RunTests) {
    Invoke-TestSuite
} elseif ($Dashboard) {
    Invoke-Dashboard
} elseif ($OpenExcel) {
    Invoke-OpenExcel
} elseif ($Notebook) {
    Invoke-Notebook
} else {
    Show-InteractiveMenu
}
