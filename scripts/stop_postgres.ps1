# Stop local portable PostgreSQL server
$pgRoot = "C:\Users\satta\pgsql"
$pgBin = "$pgRoot\bin"
$pgData = "$pgRoot\data"

Write-Host "==> Stopping PostgreSQL server..." -ForegroundColor Yellow
& "$pgBin\pg_ctl.exe" -D $pgData stop
Write-Host "==> PostgreSQL server stopped." -ForegroundColor Green
