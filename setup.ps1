# PowerShell script to clone subprojects and set up Python and Node.js environments

$repos = @{
    'TruLedgr-API'  = 'https://github.com/McGuireTechnology/TruLedgr-API.git'
    'TruLedgr-App'  = 'https://github.com/McGuireTechnology/TruLedgr-App.git'
    'TruLedgr-Docs' = 'https://github.com/McGuireTechnology/TruLedgr-Docs.git'
    'TruLedgr-Web'  = 'https://github.com/McGuireTechnology/TruLedgr-Web.git'
    'TruLedgr-Apple'  = 'https://github.com/McGuireTechnology/TruLedgr-Apple.git'
    'TruLedgr-Android'  = 'https://github.com/McGuireTechnology/TruLedgr-Android.git'
}

foreach ($name in $repos.Keys) {
    if (-not (Test-Path $name)) {
        git clone $repos[$name]
    }
    $req = Join-Path $name 'requirements.txt'
    if (Test-Path $req) {
        $venvPath = Join-Path $name '.venv'
        if (-not (Test-Path $venvPath)) {
            python -m venv $venvPath
        }
        & "$venvPath\Scripts\pip.exe" install -r $req
    }
    $pkg = Join-Path $name 'package.json'
    if (Test-Path $pkg) {
        Push-Location $name
        if (Test-Path 'yarn.lock') {
            yarn install
        } else {
            npm install
        }
        Pop-Location
    }
}

Write-Host "All subprojects cloned and Python/Node.js environments set up."
