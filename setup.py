import sys
import os
from cx_Freeze import setup, Executable
from kivy_deps import sdl2, glew

# Incluindo arquivos e pastas extras
include_files = [
    'win.kv',
    ('logos', 'logos'),
] + sdl2.dep_bins + glew.dep_bins

# Pacotes usados
packages = ['kivy', 'kivymd', 'os', 'sys','requests','ffpyplayer']

# Opções do cx_Freeze
build_exe_options = {
    "packages": packages,
    "include_files": include_files,
    "excludes": ["tkinter"],
}

# Configuração base para evitar abrir o terminal no Windows
base = "Win32GUI" if sys.platform == "win32" else None

# Setup final
setup(
    name="Master IPTV",
    version="1.0",
    description="Watch TV Direct from your PC",
    options={"build_exe": build_exe_options},
    executables=[Executable("player.py", base=base)],
)
