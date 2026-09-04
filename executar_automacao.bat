@echo off
REM ============================================================
REM  executar_automacao.bat
REM
REM  Inicia a automacao de imoveis (script.py) a partir da
REM  propria pasta do projeto. Basta dar duplo clique.
REM ============================================================

setlocal

REM Vai para a pasta onde este .bat esta (raiz do projeto).
cd /d "%~dp0"

echo.
echo ============================================================
echo  automacao_imoveis_v2 - executando
echo ============================================================
echo.

REM --- Verifica se o Python esta disponivel ---
where python >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH.
    echo        Rode primeiro o instalar_dependencias.bat.
    echo.
    pause
    exit /b 1
)

REM --- Executa a automacao ---
python script.py
set CODIGO=%errorlevel%

echo.
if %CODIGO% neq 0 (
    echo ============================================================
    echo  [ERRO] A automacao terminou com codigo %CODIGO%.
    echo         Veja as mensagens acima para entender o motivo.
    echo ============================================================
) else (
    echo ============================================================
    echo  Automacao finalizada. Veja o RESUMO DA EXECUCAO acima.
    echo  Os posts estao na pasta posts\ e as legendas em legendas\.
    echo ============================================================
)

echo.
pause
endlocal
