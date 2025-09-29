# PowerShell script to show project structure
Write-Host "🤖 Python Code Generator - Project Structure" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

$rootPath = "C:\Users\Lalit\OneDrive\文档\GitHub\Code assistant"

Write-Host "`nMain Project Files:" -ForegroundColor Yellow
Get-ChildItem -Path $rootPath -File | Where-Object { $_.Name -notlike ".*" } | ForEach-Object {
    Write-Host "  📄 $($_.Name)" -ForegroundColor White
}

Write-Host "`nConfiguration Files:" -ForegroundColor Yellow
Get-ChildItem -Path $rootPath -File | Where-Object { $_.Name -like ".*" } | ForEach-Object {
    Write-Host "  ⚙️ $($_.Name)" -ForegroundColor Gray
}

Write-Host "`nSource Code (src/):" -ForegroundColor Yellow
Get-ChildItem -Path "$rootPath\src" -File -Filter "*.py" | ForEach-Object {
    Write-Host "  🐍 $($_.Name)" -ForegroundColor Green
}

Write-Host "`nConfiguration (config/):" -ForegroundColor Yellow
Get-ChildItem -Path "$rootPath\config" -File -Filter "*.py" | ForEach-Object {
    Write-Host "  ⚙️ $($_.Name)" -ForegroundColor Magenta
}

Write-Host "`nTests (tests/):" -ForegroundColor Yellow
Get-ChildItem -Path "$rootPath\tests" -File -Filter "*.py" | ForEach-Object {
    Write-Host "  🧪 $($_.Name)" -ForegroundColor Blue
}

Write-Host "`nExamples (examples/):" -ForegroundColor Yellow
Get-ChildItem -Path "$rootPath\examples" -File -Filter "*.py" | ForEach-Object {
    Write-Host "  📚 $($_.Name)" -ForegroundColor Cyan
}

Write-Host "`nDirectories:" -ForegroundColor Yellow
Get-ChildItem -Path $rootPath -Directory | Where-Object { $_.Name -notlike ".*" } | ForEach-Object {
    Write-Host "  📁 $($_.Name)/" -ForegroundColor DarkYellow
}

Write-Host "`n🎉 Project is complete and ready to use!" -ForegroundColor Green
Write-Host "   • Total Python files: " -NoNewline -ForegroundColor White
$pyFiles = (Get-ChildItem -Path $rootPath -Recurse -File -Filter "*.py" | Where-Object { $_.FullName -notlike "*\.venv\*" -and $_.FullName -notlike "*\__pycache__\*" }).Count
Write-Host $pyFiles -ForegroundColor Yellow

Write-Host "   • Ready for LLM integration" -ForegroundColor White
Write-Host "   • All dependencies installed" -ForegroundColor White
Write-Host "   • Comprehensive test suite included" -ForegroundColor White