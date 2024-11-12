function Show-Tree ($Path = ".", $Indent = "") {
    Get-ChildItem $Path -Directory | 
    Where-Object { $_.Name -notlike ".*" -and $_.Name -ne "env" -and $_.Name -ne "backup" } | 
    ForEach-Object {
        Write-Host "$Indent$($_.Name)"
        Show-Tree $_.FullName "$Indent  "
    }
}

Write-Host "`nCognitus Project Structure:`n" -ForegroundColor Green
Show-Tree