# utils/performance_monitor.py
import time
import psutil
import streamlit as st
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Métrica individual de performance"""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    category: str = "general"

@dataclass
class QueryPerformance:
    """Métricas específicas de performance de query"""
    query_name: str
    execution_time: float
    rows_returned: int
    memory_usage: float
    cache_hit: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

class PerformanceMonitor:
    """Monitor abrangente de performance da aplicação"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetric] = []
        self.query_history: List[QueryPerformance] = []
        self.session_start = datetime.now()
        self._initialize_session_metrics()
    
    def _initialize_session_metrics(self):
        """Inicializa métricas na sessão do Streamlit"""
        if "performance_metrics" not in st.session_state:
            st.session_state.performance_metrics = []
        if "query_performance" not in st.session_state:
            st.session_state.query_performance = []
    
    @contextmanager
    def measure_time(self, operation_name: str):
        """Context manager para medir tempo de operações"""
        start_time = time.time()
        start_memory = self.get_memory_usage()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self.get_memory_usage()
            
            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            # Registra métrica
            self.record_metric(
                name=f"{operation_name}_time",
                value=execution_time,
                unit="seconds",
                category="timing"
            )
            
            if memory_delta > 0:
                self.record_metric(
                    name=f"{operation_name}_memory",
                    value=memory_delta,
                    unit="MB",
                    category="memory"
                )
    
    def measure_query_performance(func):
        """Decorator para medir performance de queries"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            start_memory = monitor.get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
                
                # Calcula métricas
                execution_time = time.time() - start_time
                memory_used = monitor.get_memory_usage() - start_memory
                rows_count = len(result) if hasattr(result, '__len__') else 0
                
                # Determina se foi cache hit
                cache_hit = execution_time < 0.1  # Heurística simples
                
                # Registra performance da query
                query_perf = QueryPerformance(
                    query_name=func.__name__,
                    execution_time=execution_time,
                    rows_returned=rows_count,
                    memory_usage=memory_used,
                    cache_hit=cache_hit
                )
                
                monitor.record_query_performance(query_perf)
                
                return result
                
            except Exception as e:
                # Registra erro de performance
                monitor.record_metric(
                    name=f"{func.__name__}_error",
                    value=1,
                    unit="count",
                    category="errors"
                )
                raise
        
        return wrapper
    
    def record_metric(self, name: str, value: float, unit: str, category: str = "general"):
        """Registra uma métrica de performance"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            category=category
        )
        
        self.metrics_history.append(metric)
        st.session_state.performance_metrics.append(metric)
        
        # Mantém histórico limitado
        if len(st.session_state.performance_metrics) > 1000:
            st.session_state.performance_metrics = st.session_state.performance_metrics[-800:]
    
    def record_query_performance(self, query_perf: QueryPerformance):
        """Registra performance de uma query"""
        self.query_history.append(query_perf)
        st.session_state.query_performance.append(query_perf)
        
        # Mantém histórico limitado
        if len(st.session_state.query_performance) > 500:
            st.session_state.query_performance = st.session_state.query_performance[-400:]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Coleta métricas do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage": cpu_percent,
                "memory_total": memory.total / (1024**3),  # GB
                "memory_available": memory.available / (1024**3),  # GB
                "memory_percent": memory.percent,
                "disk_total": disk.total / (1024**3),  # GB
                "disk_free": disk.free / (1024**3),  # GB
                "disk_percent": (disk.used / disk.total) * 100
            }
        except Exception as e:
            logger.warning(f"Erro ao coletar métricas do sistema: {e}")
            return {}
    
    def get_memory_usage(self) -> float:
        """Retorna uso atual de memória em MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0
    
    def get_streamlit_metrics(self) -> Dict[str, Any]:
        """Métricas específicas do Streamlit"""
        session_state_size = len(str(st.session_state))
        cache_size = 0
        
        # Tenta obter informações do cache
        try:
            cache_info = st.cache_data.get_stats()
            if cache_info:
                cache_size = len(cache_info)
        except Exception:
            pass
        
        return {
            "session_state_size": session_state_size,
            "cache_entries": cache_size,
            "session_duration": (datetime.now() - self.session_start).total_seconds() / 60,  # minutos
            "page_runs": st.session_state.get("_page_runs", 0)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Resumo geral de performance"""
        recent_queries = [q for q in st.session_state.query_performance 
                         if q.timestamp > datetime.now() - timedelta(minutes=30)]
        
        if not recent_queries:
            return {"message": "Nenhuma query executada recentemente"}
        
        total_queries = len(recent_queries)
        avg_time = sum(q.execution_time for q in recent_queries) / total_queries
        cache_hits = sum(1 for q in recent_queries if q.cache_hit)
        cache_hit_rate = (cache_hits / total_queries) * 100 if total_queries > 0 else 0
        
        slowest_query = max(recent_queries, key=lambda q: q.execution_time, default=None)
        fastest_query = min(recent_queries, key=lambda q: q.execution_time, default=None)
        
        return {
            "total_queries_30min": total_queries,
            "average_query_time": round(avg_time, 3),
            "cache_hit_rate": round(cache_hit_rate, 1),
            "slowest_query": {
                "name": slowest_query.query_name if slowest_query else "N/A",
                "time": round(slowest_query.execution_time, 3) if slowest_query else 0
            },
            "fastest_query": {
                "name": fastest_query.query_name if fastest_query else "N/A", 
                "time": round(fastest_query.execution_time, 3) if fastest_query else 0
            }
        }
    
    def get_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identifica gargalos de performance"""
        bottlenecks = []
        
        # Analisa queries lentas
        slow_queries = [q for q in st.session_state.query_performance 
                       if q.execution_time > 2.0]  # Mais de 2 segundos
        
        if slow_queries:
            bottlenecks.append({
                "type": "slow_queries",
                "description": f"{len(slow_queries)} queries lentas detectadas",
                "recommendation": "Considere otimizar queries ou adicionar índices",
                "queries": [(q.query_name, q.execution_time) for q in slow_queries[-5:]]
            })
        
        # Analisa uso de memória
        system_metrics = self.get_system_metrics()
        if system_metrics.get("memory_percent", 0) > 85:
            bottlenecks.append({
                "type": "high_memory",
                "description": f"Uso de memória alto: {system_metrics.get('memory_percent', 0):.1f}%",
                "recommendation": "Considere otimizar DataFrames ou limpar cache"
            })
        
        # Analisa hit rate do cache
        perf_summary = self.get_performance_summary()
        if perf_summary.get("cache_hit_rate", 100) < 50:
            bottlenecks.append({
                "type": "low_cache_hit",
                "description": f"Taxa de cache baixa: {perf_summary.get('cache_hit_rate', 0):.1f}%",
                "recommendation": "Verifique configurações de cache e TTL"
            })
        
        return bottlenecks
    
    def optimize_session_state(self):
        """Otimiza session_state removendo dados antigos"""
        # Remove métricas antigas
        cutoff_time = datetime.now() - timedelta(hours=2)
        
        if "performance_metrics" in st.session_state:
            st.session_state.performance_metrics = [
                m for m in st.session_state.performance_metrics
                if m.timestamp > cutoff_time
            ]
        
        if "query_performance" in st.session_state:
            st.session_state.query_performance = [
                q for q in st.session_state.query_performance
                if q.timestamp > cutoff_time
            ]
        
        logger.info("Session state otimizado - dados antigos removidos")
    
    def export_performance_report(self) -> Dict[str, Any]:
        """Exporta relatório completo de performance"""
        return {
            "timestamp": datetime.now().isoformat(),
            "session_duration_minutes": (datetime.now() - self.session_start).total_seconds() / 60,
            "system_metrics": self.get_system_metrics(),
            "streamlit_metrics": self.get_streamlit_metrics(),
            "performance_summary": self.get_performance_summary(),
            "bottlenecks": self.get_bottlenecks(),
            "recent_queries": [
                {
                    "name": q.query_name,
                    "time": q.execution_time,
                    "rows": q.rows_returned,
                    "cache_hit": q.cache_hit
                }
                for q in st.session_state.query_performance[-20:]  # Últimas 20 queries
            ]
        }
    
    def render_performance_dashboard(self):
        """Renderiza dashboard de performance no Streamlit"""
        st.subheader("📊 Monitor de Performance")
        
        # Métricas principais
        perf_summary = self.get_performance_summary()
        system_metrics = self.get_system_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Queries (30min)",
                perf_summary.get("total_queries_30min", 0)
            )
        
        with col2:
            st.metric(
                "Tempo Médio",
                f"{perf_summary.get('average_query_time', 0):.3f}s"
            )
        
        with col3:
            st.metric(
                "Cache Hit Rate",
                f"{perf_summary.get('cache_hit_rate', 0):.1f}%"
            )
        
        with col4:
            st.metric(
                "Memória",
                f"{system_metrics.get('memory_percent', 0):.1f}%"
            )
        
        # Gargalos
        bottlenecks = self.get_bottlenecks()
        if bottlenecks:
            st.warning("⚠️ Gargalos Detectados")
            for bottleneck in bottlenecks:
                st.error(f"**{bottleneck['type']}**: {bottleneck['description']}")
                st.info(f"💡 {bottleneck['recommendation']}")
        
        # Relatório detalhado
        with st.expander("📋 Relatório Detalhado"):
            report = self.export_performance_report()
            st.json(report)

# Instância global do monitor
performance_monitor = PerformanceMonitor()