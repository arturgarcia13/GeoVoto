# ui/components/analysis_tables.py
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional

class AnalysisTables:
    """Componente para renderização de tabelas de análise padronizadas"""
    
    def render_top_municipalities(
        self,
        data: pd.DataFrame,
        title: str,
        config: Dict,
        ascending: bool = False,
        limit: int = 5
    ):
        """Renderiza tabela de top municípios"""
        st.subheader(title)
        
        # Seleciona e ordena dados
        columns = config["columns"]
        labels = config["labels"] 
        sort_column = config["sort_column"]
        
        df_sorted = (
            data[columns]
            .sort_values(sort_column, ascending=ascending)
            .head(limit)
        )
        
        # Renomeia colunas para exibição
        df_display = df_sorted.rename(columns=labels)
        
        # Renderiza tabela
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
        
        return df_sorted
    
    def render_expandable_summary(
        self,
        data: pd.DataFrame,
        title: str,
        columns_config: Dict[str, str],
        height: int = 300,
        sort_by: Optional[str] = None
    ):
        """Renderiza tabela expansível com dados completos"""
        st.markdown(f"### {title}")
        
        with st.expander("Ver detalhes completos"):
            df_display = data.copy()
            
            # Ordena se especificado
            if sort_by and sort_by in df_display.columns:
                df_display = df_display.sort_values(sort_by, ascending=False)
            
            # Renomeia colunas
            df_display = df_display.rename(columns=columns_config)
            
            st.dataframe(
                df_display,
                use_container_width=True,
                height=height,
                hide_index=True
            )
    
    def render_comparison_table(
        self,
        data: pd.DataFrame,
        title: str,
        comparison_columns: List[str],
        value_column: str,
        format_percentages: bool = True
    ):
        """Renderiza tabela de comparação com formatação automática"""
        st.subheader(title)
        
        df_display = data[comparison_columns + [value_column]].copy()
        
        # Formata percentuais se solicitado
        if format_percentages and "Percentual" in value_column:
            df_display[value_column] = df_display[value_column].apply(
                lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A"
            )
        
        # Formata números grandes
        elif "Votos" in value_column:
            df_display[value_column] = df_display[value_column].apply(
                lambda x: f"{x:,.0f}" if pd.notnull(x) else "0"
            )
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
    
    def render_metric_cards(
        self,
        metrics: Dict[str, Dict],
        columns: int = 4
    ):
        """Renderiza cartões de métricas"""
        cols = st.columns(columns)
        
        for i, (label, metric_data) in enumerate(metrics.items()):
            with cols[i % columns]:
                st.metric(
                    label=metric_data.get("label", label),
                    value=metric_data.get("value", "N/A"),
                    delta=metric_data.get("delta"),
                    delta_color=metric_data.get("delta_color", "normal")
                )
    
    def render_summary_statistics(
        self,
        data: pd.DataFrame,
        numeric_columns: List[str],
        title: str = "📊 Estatísticas Resumidas"
    ):
        """Renderiza estatísticas descritivas"""
        st.subheader(title)
        
        # Calcula estatísticas
        stats = data[numeric_columns].describe()
        
        # Transpõe para melhor visualização
        stats_transposed = stats.transpose()
        
        # Formata números
        stats_formatted = stats_transposed.round(2)
        
        st.dataframe(
            stats_formatted,
            use_container_width=True
        )
        
        return stats_formatted
    
    def render_interactive_filter_table(
        self,
        data: pd.DataFrame,
        filter_columns: List[str],
        display_columns: List[str],
        title: str = "🔍 Dados Interativos"
    ):
        """Renderiza tabela com filtros interativos"""
        st.subheader(title)
        
        # Cria filtros
        filters = {}
        for col in filter_columns:
            if data[col].dtype == 'object' or data[col].dtype.name == 'category':
                unique_values = data[col].dropna().unique()
                filters[col] = st.multiselect(
                    f"Filtrar por {col}",
                    options=sorted(unique_values),
                    default=[]
                )
        
        # Aplica filtros
        filtered_data = data.copy()
        for col, selected_values in filters.items():
            if selected_values:  # Se algum valor foi selecionado
                filtered_data = filtered_data[
                    filtered_data[col].isin(selected_values)
                ]
        
        # Mostra contadores
        st.info(f"Mostrando {len(filtered_data)} de {len(data)} registros")
        
        # Renderiza tabela filtrada
        if len(filtered_data) > 0:
            st.dataframe(
                filtered_data[display_columns],
                use_container_width=True,
                height=400
            )
        else:
            st.warning("Nenhum registro encontrado com os filtros aplicados")