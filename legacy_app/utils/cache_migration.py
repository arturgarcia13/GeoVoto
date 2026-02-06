# utils/cache_migration.py - Migração do sistema de cache
"""
Este arquivo facilita a migração do sistema de cache antigo para o novo
Remove dependências do config/settings.py antigo
"""

import logging
from typing import Dict, Any
from config.config_manager import config_manager

logger = logging.getLogger(__name__)

class CacheMigration:
    """Utilitário para migração do sistema de cache"""
    
    @staticmethod
    def validate_migration() -> Dict[str, Any]:
        """Valida se a migração foi bem-sucedida"""
        validation_results = {
            "config_manager_available": False,
            "cache_config_valid": False,
            "ttl_values_correct": False,
            "errors": []
        }
        
        try:
            # Verifica se config_manager está disponível
            if config_manager:
                validation_results["config_manager_available"] = True
            
            # Verifica configurações de cache
            if hasattr(config_manager, 'cache'):
                validation_results["cache_config_valid"] = True
                
                # Verifica valores de TTL
                cache_config = config_manager.cache
                ttl_checks = [
                    cache_config.static_ttl > 0,
                    cache_config.semi_static_ttl > 0,
                    cache_config.dynamic_ttl > 0,
                    cache_config.volatile_ttl > 0
                ]
                
                if all(ttl_checks):
                    validation_results["ttl_values_correct"] = True
            
        except Exception as e:
            validation_results["errors"].append(str(e))
        
        return validation_results
    
    @staticmethod
    def get_legacy_compatibility_report() -> Dict[str, Any]:
        """Gera relatório de compatibilidade com sistema antigo"""
        return {
            "old_imports_removed": [
                "from config.settings import app_config",
                "app_config.cache_ttl"
            ],
            "new_imports_added": [
                "from config.config_manager import config_manager",
                "from utils.cache import cache_electoral_data"
            ],
            "cache_decorators_migrated": {
                "@simple_cached_static": "@cache_electoral_data",
                "@simple_cached_semi_static": "@cache_electoral_data", 
                "@simple_cached_dynamic": "@cache_analytics_data",
                "@st.cache_data": "@cache_geographic_data"
            },
            "benefits": [
                "Configuração centralizada por ambiente",
                "TTL dinâmico baseado no ambiente",
                "Cache específico por tipo de dado",
                "Monitoramento de performance integrado",
                "Limpeza automática de cache"
            ]
        }
    
    @staticmethod
    def log_migration_status():
        """Registra status da migração nos logs"""
        validation = CacheMigration.validate_migration()
        
        if validation["config_manager_available"]:
            logger.info("✅ Config Manager: Disponível")
        else:
            logger.error("❌ Config Manager: Não disponível")
        
        if validation["cache_config_valid"]:
            logger.info("✅ Cache Config: Válida")
            logger.info(f"TTLs configurados: "
                       f"Static={config_manager.cache.static_ttl}s, "
                       f"Semi-static={config_manager.cache.semi_static_ttl}s, "
                       f"Dynamic={config_manager.cache.dynamic_ttl}s, "
                       f"Volatile={config_manager.cache.volatile_ttl}s")
        else:
            logger.error("❌ Cache Config: Inválida")
        
        if validation["errors"]:
            for error in validation["errors"]:
                logger.error(f"❌ Erro na migração: {error}")
        
        if all([
            validation["config_manager_available"],
            validation["cache_config_valid"],
            validation["ttl_values_correct"]
        ]):
            logger.info("🎉 Migração do cache concluída com sucesso!")
        else:
            logger.warning("⚠️ Migração do cache com problemas")

# Executa validação na importação em modo debug
if config_manager.is_debug_enabled():
    CacheMigration.log_migration_status()