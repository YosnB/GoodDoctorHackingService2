# GoodDoctorHackingService ビルドスクリプト (簡易版)
# PyInstaller を使って dist フォルダを作成します

Write-Output "====================================="
Write-Output "  GoodDoctorHackingService ビルド"
Write-Output "====================================="
Write-Output ""

# 古いビルドを削除
Write-Output "[1/3] 古いビルドファイルをクリーンアップ中..."
Remove-Item -Path .\dist -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path .\build -Recurse -Force -ErrorAction SilentlyContinue
Write-Output "  ✓ 完了"
Write-Output ""

# PyInstallerでビルド
Write-Output "[2/3] PyInstallerでビルド中（コンソール付き。エラー確認用）..."
Write-Output "  - 事前に requirements.txt を使って依存をインストールしてください"
Write-Output ""

& .\.build_venv\Scripts\python.exe -m PyInstaller `
    --noconfirm `
    --onedir `
    --console `
    --name GoodDoctorHackingService `
    --add-data "logo.png;." `
    --add-data "windows;windows" `
    --hidden-import "pkg_resources.py2_warn" `
    main.py

Write-Output ""
Write-Output "[3/3] 完了 - dist フォルダを確認してください"
Write-Output "====================================="
