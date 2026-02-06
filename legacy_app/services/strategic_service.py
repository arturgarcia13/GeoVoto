# services/strategic_service.py
import pandas as pd
import streamlit as st
from typing import Dict
from dataclasses import dataclass

@dataclass  
class SupportMultipliers:
    """Multiplicadores baseados no status de apoio"""
    supports: float = 1.12
    undecided: float = 1.03
    default: float = 0.95
    
    def get_multiplier(self, status: str) -> float:
        """Retorna multiplicador baseado no status"""
        status_map = {
            "apoia": self.supports,
            "indeciso": self.undecided
        }
        return status_map.get(status, self.default)

class StrategicService:
    """Serviço para cálculos de análise estratégica"""
    
    def __init__(self):
        self.support_multipliers = SupportMultipliers()
    
    def calculate_strategic_data(
        self,
        votes_df: pd.DataFrame,
        voters_df: pd.DataFrame,
        support_df: pd.DataFrame,
        candidate_id: int
    ) -> pd.DataFrame:
        """Calcula dados estratégicos completos para um candidato"""
        
        # 1. Agrega votos do candidato por município
        candidate_votes = self._aggregate_candidate_votes(votes_df, candidate_id)
        
        # 2. Merge com dados de eleitorado
        strategic_data = self._merge_with_voters_data(candidate_votes, voters_df)
        
        # 3. Merge com dados de apoio político
        strategic_data = self._merge_with_support_data(strategic_data, support_df)
        
        # 4. Calcula métricas estratégicas
        strategic_data = self._calculate_strategic_metrics(strategic_data)
        
        return strategic_data
    
    def calculate_strategic_score(
        self,
        strategic_df: pd.DataFrame,
        weights: 'StrategicWeights'
    ) -> pd.DataFrame:
        """Calcula score estratégico baseado nos pesos fornecidos"""
        
        # Cálculo do score ponderado usando rankings percentuais
        strategic_df["Score_Estrategico"] = (
            weights.electorate * strategic_df["Eleitores_Aptos"].rank(ascending=False, pct=True) +
            weights.penetration * (100 - strategic_df["Penetracao_Atual"]).rank(ascending=False, pct=True) +
            weights.potential * strategic_df["Potencial_Crescimento"].rank(ascending=False, pct=True) +
            weights.efficiency * strategic_df["Eficiencia_Campanha"].rank(ascending=False, pct=True)
        ) / 100
        
        # Calcula posição no ranking
        strategic_df["Posicao_Ranking"] = strategic_df["Score_Estrategico"].rank(
            ascending=False, method='min'
        ).astype(int)
        
        return strategic_df
    
    def _aggregate_candidate_votes(self, votes_df: pd.DataFrame, candidate_id: int) -> pd.DataFrame:
        """Agrega votos do candidato por município"""
        
        candidate_votes = (
            votes_df[votes_df["FK_Num_Candidato"] == candidate_id]
            .groupby("FK_Cod_Municipio", as_index=False)
            .agg({"Votos_Nominais_Candidato": "sum"})
            .rename(columns={
                "FK_Cod_Municipio": "Cod_IBGE",
                "Votos_Nominais_Candidato": "Votos_Validos_Candidato"
            })
        )
        
        return candidate_votes
    
    def _merge_with_voters_data(self, votes_df: pd.DataFrame, voters_df: pd.DataFrame) -> pd.DataFrame:
        """Merge com dados de eleitorado"""
        
        voters_renamed = voters_df.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
        merged_data = pd.merge(votes_df, voters_renamed, on="Cod_IBGE", how="left")
        
        return merged_data
    
    def _merge_with_support_data(self, base_df: pd.DataFrame, support_df: pd.DataFrame) -> pd.DataFrame:
        """Merge com dados de apoio político"""
        
        support_renamed = support_df.rename(columns={"FK_Cod_Municipio": "Cod_IBGE"})
        merged_data = pd.merge(base_df, support_renamed, on="Cod_IBGE", how="left")
        
        # Preenche valores nulos de apoio com 'neutro'
        merged_data["Status_Apoio"] = merged_data["Status_Apoio"].fillna("neutro")
        
        return merged_data
    
    def _calculate_strategic_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calcula todas as métricas estratégicas"""
        
        # Garantir que não há divisões por zero
        data["Votos_Validos_Municipio"] = data["Votos_Validos_Municipio"].fillna(1)
        data["Eleitores_Aptos"] = data["Eleitores_Aptos"].fillna(1)
        data["Votos_Validos_Candidato"] = data["Votos_Validos_Candidato"].fillna(0)
        
        # 1. Impacto do apoio político
        data["Votos_Com_Impacto"] = data.apply(
            lambda row: row["Votos_Validos_Candidato"] * 
            self.support_multipliers.get_multiplier(row["Status_Apoio"]),
            axis=1
        )
        
        # 2. Ganho estimado de votos
        data["Ganho_Votos"] = data["Votos_Com_Impacto"] - data["Votos_Validos_Candidato"]
        
        # 3. Penetração atual (% dos votos válidos do município)
        data["Penetracao_Atual"] = (
            100 * data["Votos_Validos_Candidato"] / data["Votos_Validos_Municipio"]
        ).round(2)
        
        # 4. Potencial de crescimento (eleitores que ainda não votaram no candidato)
        data["Potencial_Crescimento"] = data["Eleitores_Aptos"] - data["Votos_Validos_Candidato"]
        
        # 5. Eficiência da campanha (ganho potencial / eleitorado)
        data["Eficiencia_Campanha"] = (
            100 * data["Ganho_Votos"] / data["Eleitores_Aptos"]
        ).round(2)
        
        # 6. Limita valores extremos
        data["Penetracao_Atual"] = data["Penetracao_Atual"].clip(0, 100)
        data["Eficiencia_Campanha"] = data["Eficiencia_Campanha"].clip(-100, 100)
        data["Potencial_Crescimento"] = data["Potencial_Crescimento"].clip(0, None)
        
        return data
    
    def get_strategic_recommendations(self, strategic_df: pd.DataFrame, top_n: int = 5) -> Dict[str, any]:
        """Gera recomendações estratégicas baseadas nos dados"""
        
        if strategic_df.empty:
            return {"error": "Dados insuficientes para gerar recomendações"}
        
        # Top municípios por diferentes critérios
        top_overall = strategic_df.nlargest(top_n, "Score_Estrategico")
        top_potential = strategic_df.nlargest(top_n, "Potencial_Crescimento") 
        top_efficiency = strategic_df.nlargest(top_n, "Eficiencia_Campanha")
        low_penetration = strategic_df[strategic_df["Penetracao_Atual"] < 10].nlargest(top_n, "Eleitores_Aptos")
        
        recommendations = {
            "priority_municipalities": top_overall["Cod_IBGE"].tolist(),
            "high_potential_municipalities": top_potential["Cod_IBGE"].tolist(),
            "efficient_campaign_areas": top_efficiency["Cod_IBGE"].tolist(),
            "expansion_opportunities": low_penetration["Cod_IBGE"].tolist(),
            "summary_stats": {
                "avg_penetration": strategic_df["Penetracao_Atual"].mean(),
                "total_potential_votes": strategic_df["Potencial_Crescimento"].sum(),
                "municipalities_with_support": len(strategic_df[strategic_df["Status_Apoio"] == "apoia"]),
                "municipalities_analyzed": len(strategic_df)
            }
        }
        
        return recommendations
    
    def analyze_support_impact(self, strategic_df: pd.DataFrame) -> Dict[str, float]:
        """Analisa o impacto do apoio político nos resultados"""
        
        if "Status_Apoio" not in strategic_df.columns:
            return {"error": "Dados de apoio não disponíveis"}
        
        support_analysis = {}
        
        for support_status in strategic_df["Status_Apoio"].unique():
            subset = strategic_df[strategic_df["Status_Apoio"] == support_status]
            
            if len(subset) > 0:
                support_analysis[support_status] = {
                    "municipalities_count": len(subset),
                    "avg_votes": subset["Votos_Validos_Candidato"].mean(),
                    "avg_penetration": subset["Penetracao_Atual"].mean(),
                    "avg_efficiency": subset["Eficiencia_Campanha"].mean(),
                    "total_potential": subset["Potencial_Crescimento"].sum()
                }
        
        return support_analysis