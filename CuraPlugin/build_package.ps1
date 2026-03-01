param(
    [string]$PluginName = "CrealityS1ProAutoThumbnail",
    [string]$OutputDir = "dist"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pluginDir = Join-Path $scriptDir $PluginName

if (-not (Test-Path $pluginDir)) {
    throw "Plugin folder not found: $pluginDir"
}

$pluginJsonPath = Join-Path $pluginDir "plugin.json"
if (-not (Test-Path $pluginJsonPath)) {
    throw "plugin.json not found: $pluginJsonPath"
}

$pluginJson = Get-Content $pluginJsonPath | ConvertFrom-Json
$version = [string]$pluginJson.version

$distDir = Join-Path $scriptDir $OutputDir
if (-not (Test-Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir | Out-Null
}

$zipName = "{0}-{1}.zip" -f $PluginName, $version
$zipPath = Join-Path $distDir $zipName
$stagingRoot = Join-Path $distDir "_staging"
$stagingPluginDir = Join-Path $stagingRoot $PluginName

Get-ChildItem -Path $distDir -File -Filter "$PluginName-*.zip" | Where-Object { $_.FullName -ne $zipPath } | ForEach-Object {
    try {
        Remove-Item $_.FullName -Force
    } catch {
        Write-Warning "Could not remove stale package: $($_.FullName)"
    }
}

if (Test-Path $stagingRoot) {
    try {
        Remove-Item $stagingRoot -Recurse -Force
    } catch {
        Write-Warning "Could not clear previous staging folder: $stagingRoot"
    }
}

New-Item -ItemType Directory -Path $stagingPluginDir -Force | Out-Null

Copy-Item -Path (Join-Path $pluginDir "*") -Destination $stagingPluginDir -Recurse -Force -Exclude "__pycache__"

Get-ChildItem -Path $stagingPluginDir -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path $stagingPluginDir -Recurse -File -Include "*.pyc","*.pyo" | Remove-Item -Force

$rootLicensePath = Join-Path $scriptDir "LICENSE"
$rootReadmePath = Join-Path $scriptDir "README.md"

if (Test-Path $rootLicensePath) {
    Copy-Item -Path $rootLicensePath -Destination (Join-Path $stagingPluginDir "LICENSE") -Force
}

if (Test-Path $rootReadmePath) {
    Copy-Item -Path $rootReadmePath -Destination (Join-Path $stagingPluginDir "README.md") -Force
}

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path $stagingPluginDir -DestinationPath $zipPath -CompressionLevel Optimal

Start-Sleep -Milliseconds 200

try {
    Remove-Item $stagingRoot -Recurse -Force
} catch {
    Write-Warning "Could not remove staging folder: $stagingRoot"
}

Write-Host "Created package: $zipPath"
