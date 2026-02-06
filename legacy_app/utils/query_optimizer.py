# utils/query_optimizer.py
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Tipos de query para otimização específica"""
    AGGREGATION = "aggregation"
    JOIN = "join"
    FILTER = "filter"
    GEOGRAPHIC = "geographic"
    ANALYTICAL = "analytical"

@dataclass
class QueryProfile:
    """Perfil de performance de uma query"""
    query_hash: str
    execution_count: int = 0
    avg_execution_time: float = 0.0
    last_execution: Optional[float] = None
    optimization_applied: bool = False

class QueryOptimizer:
    """Otimizador de queries SQL com padrões específicos para dados eleitorais"""
    
    def __init__(self):
        self.query_profiles: Dict[str, QueryProfile] = {}
        self.optimization_rules = self._initialize_optimization_rules()
    
    def _initialize_optimization_rules(self) -> Dict[QueryType, List[str]]:
        """Inicializa regras de otimização por tipo de query"""
        return {
            QueryType.AGGREGATION: [
                "Use SUM(), COUNT(), AVG() com GROUP BY quando possível",
                "Aplique HAVING ao invés de WHERE em agregações",
                "Use índices em colunas de GROUP BY",
                "Considere materialized views para agregações complexas"
            ],
            QueryType.JOIN: [
                "Use INNER JOIN quando possível ao invés de LEFT/RIGHT",
                "Aplique filtros antes dos JOINs",
                "Use índices em colunas de JOIN",
                "Considere CTEs para JOINs complexos"
            ],
            QueryType.FILTER: [
                "Use índices em colunas de WHERE",
                "Evite funções em WHERE clauses",
                "Use LIMIT para consultas exploratórias",
                "Aplique filtros mais seletivos primeiro"
            ],
            QueryType.GEOGRAPHIC: [
                "Use índices espaciais (GiST)",
                "Simplifique geometrias quando apropriado",
                "Use ST_DWithin ao invés de ST_Distance",
                "Considere reproje��ão apenas quando necessário"
            ],
            QueryType.ANALYTICAL: [
                "Use window functions para análises",
                "Aplique ANALYZE nas tabelas principais",
                "Considere particionamento por município/zona",
                "Use EXPLAIN ANALYZE para verificar planos"
            ]
        }
    
    def get_optimized_electoral_queries(self) -> Dict[str, str]:
        """Retorna queries otimizadas específicas para dados eleitorais"""
        return {
            "candidate_votes_by_municipality": """
                WITH candidate_aggregated AS (
                    SELECT 
                        "FK_Cod_Municipio",
                        "FK_Num_Candidato",
                        SUM("Votos_Nominais_Candidato") as total_votes,
                        COUNT(DISTINCT "Zona") as zones_count
                    FROM votacao_candidato_municipio_zona
                    WHERE "Votos_Nominais_Candidato" > 0
                    GROUP BY "FK_Cod_Municipio", "FK_Num_Candidato"
                )
                SELECT 
                    ca.*,
                    m."Nome_Municipio",
                    c."Nome_Urna"
                FROM candidate_aggregated ca
                JOIN municipio m ON ca."FK_Cod_Municipio" = m."Cod_IBGE"
                JOIN candidato c ON ca."FK_Num_Candidato" = c."Num_Candidato"
                ORDER BY ca.total_votes DESC;
            """,
            
            "turnout_analysis": """
                WITH turnout_calc AS (
                    SELECT 
                        "FK_Cod_Municipio",
                        "Eleitores_Aptos",
                        "Votos_Validos_Municipio",
                        ROUND(
                            ("Votos_Validos_Municipio"::float / NULLIF("Eleitores_Aptos", 0)) * 100, 
                            2
                        ) as turnout_percentage,
                        "Abstencao"
                    FROM manifestacao_eleitorado_municipio
                    WHERE "Eleitores_Aptos" > 0
                )
                SELECT 
                    tc.*,
                    m."Nome_Municipio",
                    CASE 
                        WHEN tc.turnout_percentage >= 90 THEN 'Alto'
                        WHEN tc.turnout_percentage >= 80 THEN 'Médio'
                        ELSE 'Baixo'
                    END as turnout_category
                FROM turnout_calc tc
                JOIN municipio m ON tc."FK_Cod_Municipio" = m."Cod_IBGE"
                ORDER BY tc.turnout_percentage DESC;
            """,
            
            "party_performance_summary": """
                WITH party_totals AS (
                    SELECT 
                        p."FK_Sigla_Partido",
                        COUNT(DISTINCT p."FK_Cod_Municipio") as municipalities_count,
                        SUM(p."Votos_Nominais_Partido") as total_votes,
                        AVG(p."Votos_Nominais_Partido") as avg_votes_per_municipality,
                        MAX(p."Votos_Nominais_Partido") as max_votes_municipality
                    FROM votos_partido_municipio p
                    WHERE p."Votos_Nominais_Partido" > 0
                    GROUP BY p."FK_Sigla_Partido"
                )
                SELECT 
                    pt.*,
                    party."Nome_Partido",
                    RANK() OVER (ORDER BY pt.total_votes DESC) as ranking_position
                FROM party_totals pt
                LEFT JOIN partido party ON pt."FK_Sigla_Partido" = party."Sigla_Partido"
                ORDER BY pt.total_votes DESC;
            """,
            
            "strategic_municipalities": """
                WITH municipality_metrics AS (
                    SELECT 
                        m."Cod_IBGE",
                        m."Nome_Municipio",
                        e."Eleitores_Aptos",
                        e."Votos_Validos_Municipio",
                        COALESCE(v.candidate_votes, 0) as candidate_votes,
                        ROUND(
                            (COALESCE(v.candidate_votes, 0)::float / NULLIF(e."Votos_Validos_Municipio", 0)) * 100,
                            2
                        ) as penetration_rate,
                        e."Eleitores_Aptos" - COALESCE(v.candidate_votes, 0) as growth_potential
                    FROM municipio m
                    JOIN manifestacao_eleitorado_municipio e ON m."Cod_IBGE" = e."FK_Cod_Municipio"
                    LEFT JOIN (
                        SELECT 
                            "FK_Cod_Municipio",
                            SUM("Votos_Nominais_Candidato") as candidate_votes
                        FROM votacao_candidato_municipio_zona
                        WHERE "FK_Num_Candidato" = %(candidate_id)s
                        GROUP BY "FK_Cod_Municipio"
                    ) v ON m."Cod_IBGE" = v."FK_Cod_Municipio"
                    WHERE e."Eleitores_Aptos" > 0
                ),
                ranked_municipalities AS (
                    SELECT 
                        *,
                        ROW_NUMBER() OVER (ORDER BY growth_potential DESC) as potential_rank,
                        ROW_NUMBER() OVER (ORDER BY "Eleitores_Aptos" DESC) as size_rank,
                        ROW_NUMBER() OVER (ORDER BY penetration_rate ASC) as opportunity_rank
                    FROM municipality_metrics
                )
                SELECT 
                    *,
                    (potential_rank + size_rank + opportunity_rank) / 3.0 as strategic_score
                FROM ranked_municipalities
                ORDER BY strategic_score;
            """,
            
            "geographic_distribution": """
                SELECT 
                    m."Cod_IBGE",
                    m."Nome_Municipio",
                    m."Unidade_Geografica",
                    COALESCE(v.total_votes, 0) as total_votes,
                    e."Eleitores_Aptos",
                    ROUND(
                        (COALESCE(v.total_votes, 0)::float / NULLIF(e."Eleitores_Aptos", 0)) * 100,
                        2
                    ) as vote_share,
                    ST_X(ST_Centroid(ST_Transform(m.geometry, 4326))) as longitude,
                    ST_Y(ST_Centroid(ST_Transform(m.geometry, 4326))) as latitude
                FROM municipio m
                JOIN manifestacao_eleitorado_municipio e ON m."Cod_IBGE" = e."FK_Cod_Municipio"
                LEFT JOIN (
                    SELECT 
                        "FK_Cod_Municipio",
                        SUM("Votos_Nominais_Candidato") as total_votes
                    FROM votacao_candidato_municipio_zona
                    WHERE "FK_Num_Candidato" = %(candidate_id)s
                    GROUP BY "FK_Cod_Municipio"
                ) v ON m."Cod_IBGE" = v."FK_Cod_Municipio"
                WHERE e."Eleitores_Aptos" > 0
                ORDER BY vote_share DESC;
            """
        }
    
    def get_performance_monitoring_queries(self) -> Dict[str, str]:
        """Queries para monitoramento de performance do banco"""
        return {
            "table_sizes": """
                SELECT 
                    schemaname,
                    tablename,
                    attname as column_name,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public'
                ORDER BY schemaname, tablename;
            """,
            
            "index_usage": """
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY idx_scan DESC;
            """,
            
            "slow_queries": """
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements
                WHERE query ILIKE '%votacao%' OR query ILIKE '%manifestacao%'
                ORDER BY mean_time DESC
                LIMIT 10;
            """
        }
    
    def optimize_query_for_type(self, query: str, query_type: QueryType) -> str:
        """Aplica otimizações baseadas no tipo de query"""
        optimized_query = query
        
        # Aplica otimizações específicas por tipo
        if query_type == QueryType.AGGREGATION:
            optimized_query = self._optimize_aggregation_query(optimized_query)
        elif query_type == QueryType.JOIN:
            optimized_query = self._optimize_join_query(optimized_query)
        elif query_type == QueryType.FILTER:
            optimized_query = self._optimize_filter_query(optimized_query)
        
        return optimized_query
    
    def _optimize_aggregation_query(self, query: str) -> str:
        """Otimizações específicas para queries de agregação"""
        # Adiciona hints de otimização
        if "GROUP BY" in query.upper() and "ORDER BY" not in query.upper():
            # Sugere ordenação para melhor performance
            query += "\n-- Considere adicionar ORDER BY nas colunas de GROUP BY"
        
        return query
    
    def _optimize_join_query(self, query: str) -> str:
        """Otimizações específicas para queries com JOIN"""
        # Verifica se há filtros que podem ser aplicados antes do JOIN
        if "WHERE" in query.upper() and "JOIN" in query.upper():
            query += "\n-- Considere aplicar filtros antes dos JOINs quando possível"
        
        return query
    
    def _optimize_filter_query(self, query: str) -> str:
        """Otimizações específicas para queries com filtros"""
        # Sugere uso de índices
        if "WHERE" in query.upper():
            query += "\n-- Certifique-se de que há índices nas colunas filtradas"
        
        return query
    
    def suggest_indexes(self) -> List[str]:
        """Sugere índices para tabelas eleitorais"""
        return [
            'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_votacao_municipio_candidato ON votacao_candidato_municipio_zona("FK_Cod_Municipio", "FK_Num_Candidato");',
            'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_votacao_candidato_votos ON votacao_candidato_municipio_zona("FK_Num_Candidato") WHERE "Votos_Nominais_Candidato" > 0;',
            'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_manifestacao_municipio ON manifestacao_eleitorado_municipio("FK_Cod_Municipio");',
            'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_apoio_municipio_candidato ON apoio_prefeito_candidato("FK_Cod_Municipio", "FK_Num_Candidato");',
            'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_partido_votos_municipio ON votos_partido_municipio("FK_Cod_Municipio", "FK_Sigla_Partido");',
            'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_candidato_nome ON candidato("Nome_Urna") WHERE "Nome_Urna" IS NOT NULL;',
            'CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_municipio_nome ON municipio("Nome_Municipio");'
        ]
    
    def get_optimization_recommendations(self, table_name: str) -> List[str]:
        """Retorna recomendações específicas para uma tabela"""
        recommendations = {
            "votacao_candidato_municipio_zona": [
                "Considere particionamento por município para grandes volumes",
                "Mantenha estatísticas atualizadas com ANALYZE regular",
                "Use índices compostos para consultas frequentes",
                "Considere índices parciais para votos > 0"
            ],
            "manifestacao_eleitorado_municipio": [
                "Índice em FK_Cod_Municipio é essencial",
                "Considere índice funcional em percentual de comparecimento",
                "Mantenha constraint CHECK em valores de eleitorado"
            ],
            "apoio_prefeito_candidato": [
                "Índice composto em (município, candidato) é recomendado",
                "Considere índice parcial por status de apoio",
                "Use enum para status de apoio se possível"
            ]
        }
        
        return recommendations.get(table_name, ["Nenhuma recomendação específica disponível"])
    
    def estimate_query_cost(self, query: str) -> Dict[str, Any]:
        """Estima custo de uma query (placeholder para integração futura)"""
        # Esta função seria integrada com EXPLAIN ANALYZE em implementação real
        return {
            "estimated_rows": "N/A",
            "estimated_cost": "N/A",
            "recommendations": ["Use EXPLAIN ANALYZE para análise detalhada"]
        }

# Instância global do otimizador
query_optimizer = QueryOptimizer()