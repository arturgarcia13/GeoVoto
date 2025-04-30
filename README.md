# 🗳️ Mapa Político - Sistema de Visualização de Votos

Este projeto faz parte da disciplina **Interfaces de Programação de Aplicações** e tem como objetivo desenvolver um **sistema interativo de visualização espacial dos votos**, com foco em apoiar a criação de **modelos de campanha eleitoral** com base em dados geográficos.

## 📍 Objetivo Geral

Desenvolver um aplicativo que permita **visualizar a distribuição de votos por região geográfica**, por meio de mapas interativos, apoiando a análise política e estratégias de campanha.

## 🎯 Objetivos Específicos

- Coletar e organizar dados eleitorais por região;
- Integrar os dados eleitorais com uma base geográfica;
- Desenvolver uma interface que permita filtrar e visualizar os dados de forma intuitiva;
- Gerar modelos de campanha baseados em análise espacial;
- Documentar todas as etapas do desenvolvimento.

---

## 🧱 Tecnologias e Ferramentas Utilizadas

| Função | Ferramenta |
|--------|------------|
| Banco de dados espacial | PostgreSQL + PostGIS |
| Servidor de mapas | GeoServer |
| Visualização no frontend | OpenLayers ou alternativa |
| Processamento geoespacial (opcional) | Python + GeoPandas |
| Backend (caso necessário) | Flask / Node.js |
| Versionamento de código | Git + GitHub |

---

## 🔄 Fases do Projeto

### 1. Introdução
Apresentação do contexto, motivação e justificativa do sistema.

### 2. Objetivos
Descrição dos objetivos geral e específicos.

### 3. Desenvolvimento do Projeto
- **Fase I – Levantamento de dados e informações**
- **Fase II – Estruturação da Base de Dados**
- **Fase III – Estruturação da Base Espacial**
- **Fase IV – Estruturação das funções do sistema**
- **Fase V – Desenvolvimento do Sistema de Informações**
- **Fase VI – Manutenção e Treinamentos**

### 4. Prazo
Duração estimada de 4 meses.

### 5. Empresa e Equipe Técnica
Equipe formada por 5 estudantes da disciplina, com divisão de tarefas descrita nos relatórios mensais.

### 6. Cronograma Físico

| Etapa | Mês 1 | Mês 2 | Mês 3 | Mês 4 |
|-------|-------|--------|--------|--------|
| Configuração do ambiente | ✅ |        |        |        |
| Criação do banco de dados |       | ✅     |        |        |
| Desenvolvimento do sistema |       |        | ✅     |        |
| Testes e entrega final     |       |        |        | ✅     |

### 7. Orçamento
Não se aplica (projeto acadêmico).

---

## 📁 Estrutura de Pastas

```
mapa-politico/
┣ 📂 data/
┃  ┣ 📂 raw/          ← Dados originais baixados
┃  ┗ 📂 processed/    ← Dados limpos e unidos
┣ 📂 notebooks/       ← Jupyter notebooks de exploração
┣ 📂 scripts/         ← Scripts Python (ETL, carga, etc)
┣ 📂 app/             ← Código futuro da aplicação
┣ 📂 docs/            ← Relatórios mensais
┣ 📜 .gitignore
┗ 📜 requirements.txt
```

---

## 👥 Equipe

- Artur Garcia
- Artur Saraiva
- Letícia Frota
- Lucas Lopes
- Iuri Sales

---

## 📝 Relatórios Mensais

Cada mês terá um relatório com:
- Atividades realizadas
- Responsável por cada tarefa
- Resultados e entregas
- Dificuldades enfrentadas

Os arquivos estarão na pasta `/docs`.

---

## 🚀 Status do Projeto

✅ Mês 1: Coleta de dados e requisitos  
⬜ Mês 2: Criação do banco de dados  
⬜ Mês 3: Desenvolvimento do sistema  
⬜ Mês 4: Testes e entrega final

---

## 📌 Observações

- Este projeto é de natureza acadêmica e não possui fins comerciais.
- O foco é a integração de dados eleitorais com dados espaciais em um sistema acessível e visual.

---
