import streamlit as st
import pandas as pd
from geovoto.services.data_service import DataService
from geovoto.ui.components.charts import (
    chart_votes_by_municipality,
    chart_political_support,
    chart_turnout,
    chart_vote_composition
)

class DashboardPage:
    """Main dashboard page."""

    def __init__(self):
        self.data_service = DataService()

    def render(self):
        st.title("📊 Dashboard de Análise Eleitoral")
        
        # Load Data
        with st.spinner("Carregando dados..."):
            try:
                data_bundle = self._load_data()
            except Exception as e:
                st.error(f"Erro ao carregar dados: {e}")
                return

        # Sidebar Filters
        st.sidebar.header("Filtros do Dashboard")
        
        # Municipality Filter
        municipios = data_bundle["municipalities"]
        municipios_list = sorted(municipios["Nome_Municipio"].unique())
        selected_municipality = st.sidebar.selectbox(
            "Município",
            ["Todos os Municípios"] + municipios_list
        )

        # Candidate Filter
        candidatos = data_bundle["candidates"]
        candidatos_list = candidatos[["Num_Candidato", "Nome_Urna"]].drop_duplicates()
        selected_candidate_name = st.sidebar.selectbox(
            "Candidato",
            candidatos_list["Nome_Urna"]
        )
        selected_candidate_id = candidatos_list[
            candidatos_list["Nome_Urna"] == selected_candidate_name
        ]["Num_Candidato"].values[0]

        # Party Filter
        partidos = data_bundle["parties"]
        partidos_list = sorted(partidos["Sigla_Partido"].unique())
        selected_party = st.sidebar.selectbox(
            "Partido",
            ["Todos"] + partidos_list
        )
        
        # Support Filter (Requires joining support data which might be heavy, skipping for now or simple list)
        selected_support = st.sidebar.selectbox(
            "Status de Apoio",
            ["Todos", "apoia", "nao apoia", "indeciso"]
        )

        # Apply Filters
        filtered_data = self._apply_filters(
            data_bundle, 
            selected_candidate_id, 
            selected_party, 
            selected_support
        )

        if not filtered_data:
            st.warning("Nenhum dado encontrado para os filtros.")
            return

        # Render KPI Metrics
        self._render_kpis(filtered_data)

        # Render Charts
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Desempenho por Município")
            chart_votes_by_municipality(
                filtered_data["votacao"], 
                data_bundle["municipalities"]
            )

        with col2:
            st.subheader("Apoio Político")
            chart_political_support(
                filtered_data["votacao"],
                filtered_data["apoio"]
            )

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Comparecimento")
            chart_turnout(
                filtered_data["voters"],
                data_bundle["municipalities"]
            )

        with col4:
            chart_vote_composition(
                filtered_data["voters"],
                data_bundle["municipalities"],
                selected_municipality
            )

    def _load_data(self):
        """Loads all necessary dataframes via DataService."""
        return {
            "municipalities": self.data_service.get_municipalities_data(),
            "candidates": self.data_service.get_candidates_data(),
            "parties": self.data_service.get_parties_data(),
            "voters": self.data_service.get_voters_data(),
            "support": self.data_service.get_support_data(),
            "votes_summary": self.data_service.get_votes_summary() # This one gives total votes per candidate per muni
        }

    def _apply_filters(self, data, candidate_id, party, support_status):
        """Applies filters to the datasets."""
        # Main voting table (we need to construct it or use a view)
        # Using DataService.get_candidate_votes ? No, that's aggregated.
        # We need raw-ish data for charts using filters.
        # Let's use the votes_summary which has FK_Num_Candidato
        
        votes = data["votes_summary"] # has FK_Cod_Municipio, FK_Num_Candidato, Total_Votos
        # We need to adapt the charts to expect this schema, OR fetch detailed data.
        # The charts expect 'Votos_Nominais_Candidato' (detailed) or 'Votos_Validos_Candidato' (aggregated?)
        # Let's map Total_Votos -> Votos_Validos_Candidato for compatibility
        votes = votes.rename(columns={"Total_Votos": "Votos_Validos_Candidato"})

        # Filter by Candidate
        votes = votes[votes["FK_Num_Candidato"] == candidate_id]

        # Filter Support
        support_df = data["support"]
        if support_status != "Todos":
            support_df = support_df[support_df["Status_Apoio"] == support_status]
            # Filter votes based on supported municipalities
            # Logic: We need support info for the candidate in the municipality
            # support table: FK_Cod_Municipio, FK_Num_Candidato, Status_Apoio
            
            # Since we already filtered votes by candidate_id, we can filter support by candidate_id too
            support_df = support_df[support_df["FK_Num_Candidato"] == candidate_id]
            valid_munis = support_df["FK_Cod_Municipio"].unique()
            votes = votes[votes["FK_Cod_Municipio"].isin(valid_munis)]
            
            # Also filter support_df itself for the chart
        
        # Filter Party (this is tricky because votes table usually doesn't have party column, candidate table does)
        # But we already filtered by specific candidate ID, so party is implicit.
        # The Party filter in UI seems to filter the list of candidates? In the original code it filtered the dataframe.
        # If the user selected a candidate, the party filter is redundant unless it's for "Show all candidates of party X". 
        # But logic says: Select Candidate -> show their data.
        # I'll ignore party filter for the specific candidate view, assuming candidate selection is primary.

        return {
            "votacao": votes,
            "apoio": support_df,
            "voters": data["voters"]
        }

    def _render_kpis(self, data):
        """Renders key performance indicators."""
        total_votes = data["votacao"]["Votos_Validos_Candidato"].sum()
        total_munis = data["votacao"]["FK_Cod_Municipio"].nunique()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Votos", f"{total_votes:,.0f}")
        col2.metric("Municípios com Votos", total_munis)
        # col3.metric("Ticket Médio", ...)
