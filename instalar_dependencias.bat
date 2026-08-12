@echo off
REM ============================================================
REM  instalar_dependencias.bat
REM
REM  Instala as dependencias do projeto automacao_imoveis_v2:
REM    - Pillow (manipulacao de imagem)
REM    - Playwright (raspagem do site de leiloes)
REM    - Chromium (navegador usado pelo Playwright)
REM
REM  Uso: duplo clique, ou rodar do terminal na raiz do projeto.
REM ============================================================

setlocal

cd /d "%~dp0"

echo.
echo ============================================================
echo  automacao_imoveis_v2 - instalador de dependencias
echo ============================================================
echo.

REM --- 1. Verifica Python ---
where python >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH.
    echo        Instale o Python 3.10+ de https://www.python.org/downloads/
    echo        e marque a opcao "Add Python to PATH" na instalacao.
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] Python detectado: %PYVER%

REM --- 2. Garante que pip esta atualizado ---
echo.
echo [1/4] Atualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERRO] Falha ao atualizar pip.
    pause
    exit /b 1
)

REM --- 3. Instala pacotes Python ---
echo.
echo [2/4] Instalando Pillow e Playwright...
python -m pip install pillow playwright
if errorlevel 1 (
    echo [ERRO] Falha ao instalar pacotes Python.
    pause
    exit /b 1
)

REM --- 4. Baixa o Chromium do Playwright ---
echo.
echo [3/4] Baixando Chromium do Playwright (pode demorar alguns minutos)...
python -m playwright install chromium
if errorlevel 1 (
    echo [ERRO] Falha ao instalar o Chromium do Playwright.
    pause
    exit /b 1
)

REM --- 5. Verificacao final ---
echo.
echo [4/4] Verificando instalacao...
python -c "from playwright.sync_api import sync_playwright; from PIL import Image; p = sync_playwright().start(); b = p.chromium.launch(headless=True); b.close(); p.stop(); print('Tudo certo - Playwright + Chromium + Pillow funcionando.')"
if errorlevel 1 (
    echo.
    echo [AVISO] A verificacao final falhou. Rode o comando acima manualmente
    echo         pra ver o erro completo.
) else (
    echo.
    echo ============================================================
    echo  Instalacao concluida com sucesso!
    echo.
    echo  Agora voce pode rodar a automacao com:
    echo      python script.py
    echo ============================================================
)

echo.
pause
endlocal