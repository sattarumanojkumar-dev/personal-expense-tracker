# Start local portable PostgreSQL server
$pgRoot = "C:\Users\satta\pgsql"
$pgBin = "$pgRoot\bin"
$pgData = "$pgRoot\data"
$pgLog = "$pgRoot\logfile.log"

Write-Host "==> Checking PostgreSQL Setup..." -ForegroundColor Cyan

if (!(Test-Path "$pgData\PG_VERSION")) {
    Write-Host "==> Initializing PostgreSQL data cluster at $pgData..." -ForegroundColor Yellow
    & "$pgBin\initdb.exe" -D $pgData -U postgres -A trust -E utf8
}

Write-Host "==> Starting PostgreSQL server on port 5432..." -ForegroundColor Green
& "$pgBin\pg_ctl.exe" -D $pgData -l $pgLog start

Start-Sleep -Seconds 2

# Check if expense_tracker_db exists, if not create it
& "$pgBin\psql.exe" -U postgres -lqt | Select-String -Pattern "expense_tracker_db" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "==> Creating database 'expense_tracker_db'..." -ForegroundColor Yellow
    & "$pgBin\createdb.exe" -U postgres expense_tracker_db
}

Write-Host "==> PostgreSQL is running and ready!" -ForegroundColor Green
