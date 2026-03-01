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

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path $pluginDir -DestinationPath $zipPath -CompressionLevel Optimal

Write-Host "Created package: $zipPath"
