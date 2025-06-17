import sys
from cx_Freeze import setup, Executable

# --- DADOS DO JOGO ---
nome_do_jogo = "Frontline Fury"
versao = "1.0"
descricao = "Um jogo de tiro 2D em plataforma."

# --- ARQUIVOS E PASTAS A INCLUIR ---
incluir_arquivos = [
    'recursos/',             # Pasta de recursos (imagens, sons, ícones)
    'log.dat',
    'level1_data.csv',
    'level2_data.csv',
    'level3_data.csv'
]

# --- PACOTES NECESSÁRIOS (incluindo os nativos que cx_Freeze ignora) ---
pacotes_necessarios = [
    'pygame',
    'os',
    'random',
    'csv',
    'json',
    'pyttsx3',
    'speech_recognition',
    'tkinter',
    'pyaudio',
    'aifc',
    'chunk',
    'wave',
    'audioop'
]

# --- OPÇÕES DO BUILD ---
opcoes_build_exe = {
    'packages': pacotes_necessarios,
    'include_files': incluir_arquivos
}

# --- CONFIGURAÇÃO DE BASE (para remover janela de terminal no Windows) ---
base = "Win32GUI" if sys.platform == "win32" else None

# --- DEFINIÇÃO DO EXECUTÁVEL ---
executavel = Executable(
    script="main.py",
    base=base,
    target_name=f"{nome_do_jogo}.exe",
    icon="recursos/frontlinefury.ico"  # Atenção: precisa ser .ico, não .png
)

# --- CHAMADA FINAL PARA SETUP ---
setup(
    name=nome_do_jogo,
    version=versao,
    description=descricao,
    options={"build_exe": opcoes_build_exe},
    executables=[executavel]
)
