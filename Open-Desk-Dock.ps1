param([int]$Port = 8768)
$ErrorActionPreference = 'Stop'
$projectDir = $PSScriptRoot
$viewerUrl = "http://127.0.0.1:$Port/docs/desk-dock.html"
try {
    $page = Invoke-WebRequest -Uri $viewerUrl -TimeoutSec 2
    if ($page.Content -notmatch 'Precision 5680') { throw 'The selected port serves a different application. Choose another -Port.' }
} catch {
    if ($_.Exception.Message -like '*different application*') { throw }
    $pythonPath = (Get-Command python -ErrorAction Stop).Source
    Start-Process -FilePath $pythonPath -ArgumentList @('-m', 'http.server', "$Port", '--bind', '127.0.0.1', '--directory', ('"' + $projectDir + '"')) -WindowStyle Hidden | Out-Null
    $ready = $false
    for ($attempt = 0; $attempt -lt 20; $attempt++) {
        try {
            $page = Invoke-WebRequest -Uri $viewerUrl -TimeoutSec 1
            if ($page.Content -match 'Precision 5680') { $ready = $true; break }
        } catch { Start-Sleep -Milliseconds 200 }
    }
    if (-not $ready) { throw "The local viewer did not start on port $Port." }
}
Start-Process $viewerUrl
