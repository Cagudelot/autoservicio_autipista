"""
Punto de entrada para Streamlit Cloud
"""
import sys
import os

# Configurar paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

# Ejecutar la app principal
from src.app import main

# Llamar a la función principal
main()
