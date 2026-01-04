"""
Módulo de Empleados
"""
from src.modules.empleados.registro import render as render_registro
from src.modules.empleados.turnos import render as render_turnos
from src.modules.empleados.turnos_hoy import render as render_turnos_hoy
from src.modules.empleados.gestion_turnos_2 import render as render_gestion_turnos_2

__all__ = ['render_registro', 'render_turnos', 'render_turnos_hoy', 'render_gestion_turnos_2']
