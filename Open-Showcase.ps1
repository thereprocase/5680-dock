param([int]$Port = 8769)
$ErrorActionPreference = 'Stop'
$siteDir = Join-Path $PSScriptRoot 'docs'
$viewerUrl = "http://127.0.0.1:$Port/"
try {
    $page = Invoke-WebRequest -Uri $viewerUrl -TimeoutSec 2
    if ($page.Content -notmatch '5680 Dock') { throw 'This port serves another application. Choose another -Port.' }
} catch {
    if ($_.Exception.Message -like '*another application*') { throw }
    $pythonPath = (Get-Command python -ErrorAction Stop).Source
    Start-Process -FilePath $pythonPath -ArgumentList @('-m','http.server',"$Port",'--bind','127.0.0.1','--directory',('"' + $siteDir + '"')) -WindowStyle Hidden | Out-Null
    Start-Sleep -Milliseconds 700
}
Start-Process $viewerUrl
