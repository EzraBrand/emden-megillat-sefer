# Download the Pninim text of Megillat Sefer (Bick 1979 base, GFDL 1.3) into source\pninim\.
# Run from anywhere:  powershell -ExecutionPolicy Bypass -File "<this file>"
$ErrorActionPreference = "Stop"
$out = Join-Path (Split-Path $PSScriptRoot -Parent) "source\pninim"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$base = "https://gitlab.com/pninim.org/pninim/-/raw/master/" + [uri]::EscapeDataString("קורות_חיים") + "/" + [uri]::EscapeDataString("מגילת_ספר") + "/"
$names = @("index","שער","הקדמת_המוציא_לאור","הקדמה","מבוא","פתיחה","א","ב","ג","ד","ה","ו","ז","ח","נספחים",
           "מפתח_השמות","מפתח_ענינים","מפתח_ערים_וארצות","מפתח_הספרים")
foreach ($n in $names) {
    $dest = Join-Path $out ($n + ".txt")
    curl.exe -sS -f -o $dest ($base + [uri]::EscapeDataString($n))
    Write-Host ("{0,-22} {1,8} bytes" -f $n, (Get-Item $dest).Length)
}
Write-Host "done"
