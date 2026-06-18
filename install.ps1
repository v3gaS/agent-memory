#Requires -Version 5.1
<#
.SYNOPSIS
  Bootstrap agent-memory into a target project (Windows / PowerShell).

.EXAMPLE
  .\install.ps1 -Target C:\dev\my-app

.EXAMPLE
  irm https://raw.githubusercontent.com/YOUR_ORG/agent-memory/main/install.ps1 | iex; Install-AgentMemory -Target .
#>
param(
    [Parameter(Mandatory = $true)]
    [string] $Target,

    [switch] $Local,
    [string] $Repo = $env:AGENT_MEMORY_INSTALL_REPO,
    [string] $Ref = $(if ($env:AGENT_MEMORY_INSTALL_REF) { $env:AGENT_MEMORY_INSTALL_REF } else { "main" }),
    [string] $Config,
    [switch] $Yes,
    [switch] $Force,
    [switch] $NoVerify,
    [ValidateSet("", "python", "node", "go", "rust")]
    [string] $Preset = "",
    [string] $ProjectName,
    [string] $Stack,
    [string] $PrimaryConfig,
    [string] $SrcRoot,
    [string] $TestCommand
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $Repo) {
    $defaultsFile = Join-Path $ScriptDir "config\install.defaults.env"
    if (Test-Path $defaultsFile) {
        Get-Content $defaultsFile | ForEach-Object {
            if ($_ -match '^AGENT_MEMORY_INSTALL_REPO=(.+)$') { $Repo = $Matches[1].Trim() }
        }
    }
    if (-not $Repo) { $Repo = "https://github.com/YOUR_ORG/agent-memory.git" }
}

function Write-Log($msg) { Write-Host "agent-memory: $msg" }

function Ensure-PythonTooling {
    if (-not (Get-Command python -ErrorAction SilentlyContinue) -and -not (Get-Command python3 -ErrorAction SilentlyContinue)) {
        throw "python not found on PATH"
    }
    $py = if (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { "python" }
    & $py -c "import yaml" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Log "installing PyYAML ..."
        & $py -m pip install --user pyyaml
    }
    if (-not $NoVerify) {
        & $py -c "import pytest" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Log "installing pytest ..."
            & $py -m pip install --user pytest
        }
    }
    return $py
}

function Resolve-ScaffoldRoot {
    if ($env:AGENT_MEMORY_SCAFFOLD_ROOT) { return $env:AGENT_MEMORY_SCAFFOLD_ROOT }
    if ($Local -or (Test-Path (Join-Path $ScriptDir "apply.py"))) { return $ScriptDir }
    $tmp = Join-Path $env:TEMP ("agent-memory-" + [guid]::NewGuid().ToString("n"))
    Write-Log "cloning $Repo ($Ref) ..."
    git clone --depth 1 --branch $Ref $Repo $tmp
    return $tmp
}

function Apply-Preset {
    switch ($Preset) {
        "python" {
            if (-not $Stack) { $script:Stack = "Python 3.12+ application" }
            if (-not $PrimaryConfig) { $script:PrimaryConfig = "config/settings.yaml" }
            if (-not $SrcRoot) { $script:SrcRoot = "src/" }
            if (-not $TestCommand) { $script:TestCommand = "pytest -q" }
        }
        "node" {
            if (-not $Stack) { $script:Stack = "Node.js / TypeScript application" }
            if (-not $PrimaryConfig) { $script:PrimaryConfig = ".env" }
            if (-not $SrcRoot) { $script:SrcRoot = "src/" }
            if (-not $TestCommand) { $script:TestCommand = "npm test" }
        }
        "go" {
            if (-not $Stack) { $script:Stack = "Go application" }
            if (-not $PrimaryConfig) { $script:PrimaryConfig = "config.yaml" }
            if (-not $SrcRoot) { $script:SrcRoot = "./" }
            if (-not $TestCommand) { $script:TestCommand = "go test ./..." }
        }
        "rust" {
            if (-not $Stack) { $script:Stack = "Rust application" }
            if (-not $PrimaryConfig) { $script:PrimaryConfig = ".env" }
            if (-not $SrcRoot) { $script:SrcRoot = "src/" }
            if (-not $TestCommand) { $script:TestCommand = "cargo test" }
        }
    }
}

Apply-Preset
if ($Yes -and -not $Config -and -not $ProjectName) {
    $ProjectName = Split-Path -Leaf (Resolve-Path $Target -ErrorAction SilentlyContinue).Path
    if (-not $ProjectName) { $ProjectName = Split-Path -Leaf $Target }
}

New-Item -ItemType Directory -Force -Path $Target | Out-Null
$Target = (Resolve-Path $Target).Path

$py = Ensure-PythonTooling
$scaffoldRoot = Resolve-ScaffoldRoot
$apply = Join-Path $scaffoldRoot "apply.py"
if (-not (Test-Path $apply)) { throw "apply.py not found at $apply" }

$argsList = @($apply, "--target", $Target)
if ($Config) { $argsList += @("--config", $Config) }
if ($Yes) { $argsList += "--no-prompt" }
if ($Force) { $argsList += "--force" }
if ($ProjectName) { $argsList += @("--project-name", $ProjectName) }
if ($Stack) { $argsList += @("--stack", $Stack) }
if ($PrimaryConfig) { $argsList += @("--primary-config", $PrimaryConfig) }
if ($SrcRoot) { $argsList += @("--src-root", $SrcRoot) }
if ($TestCommand) { $argsList += @("--test-command", $TestCommand) }

Write-Log "running apply.py -> $Target"
& $py @argsList

if (-not $NoVerify) {
    Push-Location $Target
    try {
        Write-Log "verifying docs integrity ..."
        & $py scripts/docs_integrity.py
        Write-Log "running docs regression tests ..."
        & $py -m pytest tests/test_docs_integrity.py -q
    } finally {
        Pop-Location
    }
}

Write-Log "done"
