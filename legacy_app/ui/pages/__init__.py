# ui/pages/__init__.py
"""
Módulo de páginas da aplicação

Este módulo contém todas as páginas da aplicação organizadas
em classes que herdam de BasePage.
"""

from .base_page import BasePage
from .dashboard_page import DashboardPage  
from .geographic_page import GeographicPage
from .strategic_page import StrategicPage
from .users_page import UsersPage

__all__ = [
    'BasePage',
    'DashboardPage',
    'GeographicPage', 
    'StrategicPage',
    'UsersPage'
]