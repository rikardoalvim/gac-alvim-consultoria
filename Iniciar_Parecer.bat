@echo off
setlocal
set "BASE=C:\DOCS\PARECER"
set "VENV=%BASE%\.venv"
if not exist "%BASE%" (
  mkdir "%BASE%"
)

:: cria venv se não existir
if not exist "%VENV%\Scripts\python.exe" (
  echo [1/3] Criando ambiente virtual...
  py -m venv "%VENV%"
)

echo [2/3] Atualizando pip e instalando dependencias...
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install streamlit reportlab PyPDF2 openai python-docx


echo [3/3] Iniciando o app...
cd /d "%BASE%"
"%VENV%\Scripts\python.exe" -m streamlit run parecer_app.py
endlocal
