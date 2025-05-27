<p align="center">
  <img src="./Imagens/capa2.png" alt="Banner do Projeto" width="100%">
</p>


# 🛡️ Detecção de Fraudes nas Entregas do Walmart

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://walmart-delivery-fraud-analysis-dashboard.streamlit.app/)
[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📌 Visão Geral e Contexto do Problema

O aumento expressivo das compras online nos últimos anos trouxe grandes benefícios para empresas e consumidores, mas também revelou vulnerabilidades operacionais, especialmente nos processos de entrega. Empresas de grande porte, como o Walmart, enfrentam desafios crescentes relacionados à confiabilidade da entrega, perdas logísticas e fraudes.

### 🎯 Problema Central
As fraudes em entregas ocorrem quando há inconsistências entre o que foi enviado e o que o cliente declara ter recebido, podendo envolver:
- **Motoristas desonestos** que desviam produtos
- **Clientes fraudulentos** que fazem reclamações falsas
- **Falhas sistêmicas** nos processos de verificação
- **Vulnerabilidades regionais** e temporais

### 📈 Impacto do Problema
- **Prejuízos financeiros** diretos com reposição de produtos
- **Perda de confiança** dos clientes legítimos
- **Aumento de custos operacionais** com investigações
- **Deterioração da marca** e reputação da empresa

Este projeto busca entender a origem dessas falhas a partir de um conjunto de dados reais da operação do Walmart na região Central da Flórida, utilizando técnicas avançadas de ciência de dados para extrair padrões de comportamento e propor soluções com embasamento técnico e estatístico.

---

## 🧭 Introdução

Este projeto tem como objetivo aplicar **ciência de dados avançada** para detectar, analisar e mitigar ocorrências de fraudes em entregas realizadas pelo Walmart na região Central da Flórida. A iniciativa se apoia em um conjunto de dados realistas, técnicas estatísticas, machine learning e estratégias de visualização de dados para propor soluções concretas e baseadas em evidências.

### 🏗️ Arquitetura do Projeto

```
📁 Projeto Walmart Fraud Detection/
├── 📊 Dashboard/                    # Dashboard Streamlit interativo
│   ├── app.py                      # Aplicação principal
│   ├── pages/                      # Módulos de páginas
│   │   ├── panorama.py             # Visão geral
│   │   ├── analise_temporal.py     # Análise temporal
│   │   ├── categorias_itens.py     # Análise de produtos
│   │   ├── regioes_entregadores.py # Análise regional
│   │   ├── padroes_ocultos.py      # Machine Learning
│   │   ├── diagnostico.py          # Diagnóstico de responsabilidade
│   │   ├── evolucao.py             # Tendências temporais
│   │   └── recomendacoes.py        # Ações recomendadas
│   ├── utils/                      # Utilitários
│   │   ├── graphics.py             # Funções de visualização
│   │   ├── loaders.py              # Carregamento de dados
│   │   └── filters.py              # Filtros e transformações
│   └── config/                     # Configurações
│       └── style_config.py         # Estilos e temas
├── 📂 Notebooks/                   # Análises Jupyter
├── 📄 Dados/                       # Arquivos CSV originais
├── 🗄️ Database/                    # Base SQLite
│   └── walmart_fraudes.db          # Banco de dados principal
├── 📖 Documentação/                # Documentação técnica
├── 📋 Relatório/                   # Relatórios finais
└── 🎨 Imagens/                     # Assets visuais
```

A estrutura do projeto está organizada da seguinte forma:

- **`Notebooks/`**: Contém os Jupyter Notebooks utilizados para cada etapa da análise (EDA, modelagem, avaliação, etc.).
- **`Dados/`**: Inclui os arquivos CSV com os dados brutos.
- **`Database/`**: Armazena a base de dados em SQLite utilizada para realizar consultas SQL e cruzamentos entre tabelas.
- **`Documentação/`**: Textos de apoio e descrições técnicas.
- **`Relatório/`**: Versões PDF e Markdown do relatório completo.
- **`Dashboard/`**: Dashboard desenvolvido em Streamlit para análise interativa (atualização da implementação original em Power BI).

### 🛠️ Stack Tecnológica

**Backend & Análise:**
- **Python 3.8+** - Linguagem principal
- **Pandas & NumPy** - Manipulação de dados
- **SQLite** - Banco de dados relacional
- **Scikit-learn** - Machine Learning
- **Plotly & Seaborn** - Visualização avançada

**Dashboard & Interface:**
- **Streamlit** - Framework web para dashboards
- **Plotly Dash** - Gráficos interativos
- **CSS/HTML** - Customização visual
- **Responsive Design** - Interface adaptável

**DevOps & Deployment:**
- **Streamlit Cloud** - Deploy automático
- **Git/GitHub** - Controle de versão
- **Docker** - Containerização (opcional)

💡 **Todos os scripts estão comentados e versionados para facilitar a reprodutibilidade.**

<p align="center">
  <a href="README.MD">📘 README</a> •
  <a href="./Relatório/RELATORIO.md">📊 Relatório</a> •
  <a href="./Instrucoes/INSTRUCOES.md">📂 Documentação</a> •
  <a href="https://walmart-delivery-fraud-analysis-dashboard.streamlit.app/">🚀 Dashboard Live</a>
</p>

---

## 🔍 Metodologia e Etapas da Análise

### 🧪 1. Análise Exploratória dos Dados (EDA)

**Estrutura dos Dados:**
- **`orders`** - 10.000 registros de pedidos e entregas
- **`drivers`** - 500 motoristas com perfis comportamentais
- **`customers`** - 1.000 clientes únicos
- **`missing_items`** - 5.000 relatos de itens não entregues
- **`products`** - 200 produtos do catálogo

**Processo de Análise:**
- ✅ Análise das tabelas: `orders`, `drivers`, `customers`, `missing_items`, `products`
- ✅ Verificação de dados ausentes e integridade relacional entre IDs
- ✅ Identificação de regiões e horários com maior volume de reclamações (ex.: Altamonte Springs, Apopka e período da madrugada)
- ✅ Análise de recorrência entre motoristas e clientes com falhas
- ✅ Combinação via SQL de múltiplas tabelas para cruzar entregas, itens não recebidos e perfis de motoristas

**Descobertas Principais:**
- 🚨 **Regiões críticas:** Altamonte Springs (8.2% fraude), Apopka (7.8% fraude)
- ⏰ **Horários vulneráveis:** 0h-5h (taxa 3x maior que média)
- 👥 **Motoristas reincidentes:** 23 motoristas com taxa >10% de problemas
- 🛒 **Produtos alvo:** Chicken Breast, Peanut Butter, Ground Coffee

**Técnicas Aplicadas:**
```python
# Exemplo de análise de correlação temporal
fraud_by_hour = orders.groupby('delivery_hour').agg({
    'items_missing': 'sum',
    'order_id': 'count'
}).reset_index()
fraud_rate = (fraud_by_hour['items_missing'] / fraud_by_hour['order_id'] * 100)
```

### 🧠 2. Detecção de Padrões de Fraude

**Algoritmos Implementados:**

**🌲 Isolation Forest**
- Detecção de anomalias em comportamento de motoristas
- Identificação de outliers em padrões de entrega
- Precisão: 87% na detecção de casos suspeitos

**🌳 Random Forest**
- Classificação de pedidos de alto risco
- Feature importance para fatores de fraude
- AUC-ROC: 0.91

**📊 K-Means Clustering**
- Segmentação de motoristas por perfil de risco
- Agrupamento de regiões por similaridade
- 4 clusters distintos identificados

**Processo de Modelagem:**
- ✅ Aplicação de Isolation Forest e Random Forest para detectar entregadores com padrões fora da curva
- ✅ Análise de divergência entre itens entregues e recebidos
- ✅ Clusterização de motoristas reincidentes por métricas de comportamento
- ✅ Destacam-se motoristas como Dana Ferguson e Daniel Hall, com altas taxas de pedidos problemáticos

**Variáveis Preditivas:**
- `delivery_hour` - Horário da entrega
- `driver_trips_count` - Experiência do motorista
- `region` - Localização geográfica
- `product_category` - Tipo de produto
- `customer_order_history` - Histórico do cliente

### ⚖️ 3. Avaliação de Causas e Responsabilidades

**📍 Análise Regional:**
```
Região               Taxa Fraude   Volume    Risk Score
Altamonte Springs    8.2%          1,247     Alto
Apopka              7.8%          1,156     Alto
Winter Park         3.1%          2,341     Médio
Orlando Center      2.8%          3,892     Baixo
```

**👨‍💼 Perfil de Motoristas Críticos:**
- **Dana Ferguson:** 47 relatos em 156 entregas (30.1%)
- **Daniel Hall:** 52 relatos em 203 entregas (25.6%)
- **Mark Wilson:** 38 relatos em 167 entregas (22.8%)

**🕐 Padrões Temporais:**
- **Madrugada (0h-5h):** 12.4% taxa de fraude
- **Manhã (6h-11h):** 3.2% taxa de fraude
- **Tarde (12h-17h):** 2.8% taxa de fraude
- **Noite (18h-23h):** 4.1% taxa de fraude

**Principais Achados:**
- ✅ Regiões críticas identificadas: Altamonte Springs e Apopka
- ✅ Horários com maior taxa de falha: entre 0h e 5h
- ✅ Produtos mais visados: Chicken Breast, Peanut Butter, Ground Coffee
- ✅ Clientes e motoristas reincidentes apontados como possíveis causadores de fraudes recorrentes
- ✅ Evolução temporal indica crescimento dos casos com o tempo

---

## 🎯 Dashboard Interativo

### 🚀 Acesso Online
**[🔗 Dashboard ao Vivo](https://walmart-delivery-fraud-analysis-dashboard.streamlit.app/)**

### 📊 Funcionalidades Implementadas

**Ferramentas utilizadas:** Streamlit (evolução da proposta original em Power BI/Google Sheets/Looker Studio para uma solução mais robusta e interativa)

**Métricas apresentadas:**
- ✅ Total de pedidos com falha por período
- ✅ Mapa de calor por cidade e região
- ✅ Produtos mais relatados como não entregues
- ✅ Ranking de motoristas e clientes com maiores ocorrências
- ✅ Filtros por hora, local, cliente, produto e motorista

**1. 🏠 Panorama Geral**
- KPIs principais em tempo real
- Tendência de fraudes com linha de regressão
- Distribuição por categoria de produtos
- Lista completa de motoristas ranqueados

**2. ⏱️ Análise Temporal**
- Heatmap interativo hora x dia da semana
- Médias móveis (7 e 30 dias)
- Detecção de anomalias temporais
- Análise de sazonalidade

**3. 📦 Produtos & Categorias**
- Treemap hierárquico com emojis
- Correlação preço × fraude
- Rankings interativos
- Filtros por categoria e impacto

**4. 🗺️ Regiões & Entregadores**
- Análise geoespacial (quando disponível)
- Perfis detalhados de motoristas
- Detecção de comportamento anômalo
- Correlações demográficas

**5. 🔍 Padrões Ocultos**
- Matriz de correlação interativa
- Clusterização com visualização 2D
- Análise de padrões sequenciais
- Machine Learning em tempo real

**6. 🩺 Diagnóstico de Responsabilidade**
- Mapa de correlações motorista × produto
- Diagrama de Sankey para fluxos
- Tabela cruzada de análise
- Atribuição quantitativa de responsabilidade

**7. 📈 Evolução e Tendências**
- Comparação entre períodos
- Projeções baseadas em tendências
- Identificação de pontos de inflexão
- Análise de ciclos sazonais

**8. 💡 Recomendações Inteligentes**
- Matriz esforço × impacto
- Plano de ação em fases
- ROI estimado para cada medida
- Métricas de acompanhamento

### 🎨 Interface e Experiência

**Design Responsivo:**
- 📱 Compatível com mobile e desktop
- 🌙 Modo escuro/claro
- ⚡ Carregamento otimizado
- 🎯 Interface intuitiva

**Interatividade Avançada:**
- 🔄 Filtros dinâmicos globais
- 📊 Gráficos interativos com Plotly
- 📥 Exportação de dados (CSV, PDF)
- 🔍 Drill-down em análises

---

## ✅ Recomendações e Medidas Preventivas

### 🛠️ Soluções Técnicas Implementáveis

| 🛠️ Medida                         | 💡 Justificativa                                                | 📉 Redução Estimada | 💰 Investimento | ⏱️ Prazo |
|----------------------------------|------------------------------------------------------------------|----------------------|-----------------|-----------|
| **Validação com foto obrigatória** | Comprovação visual no momento da entrega                        | 12–18%               | Baixo           | 1-3 meses |
| **QR Code dinâmico + PIN**         | Autenticação segura e exclusiva por pedido                      | 8–12%                | Médio           | 2-4 meses |
| **Auditoria de motoristas**        | Foco em reincidentes com alta taxa de falha                     | 6–10%                | Baixo           | 1 mês     |
| **Monitoramento geotemporal**      | Prevenção em zonas e períodos críticos                          | 5–8%                 | Alto            | 4-6 meses |
| **IA para detecção em tempo real** | Algoritmos preditivos para flagging automático                  | 10–15%               | Alto            | 6-12 meses|
| **Sistema de scoring integrado**   | Pontuação de risco para pedidos e motoristas                    | 8–12%                | Médio           | 3-6 meses |
| **📊 Total combinado estimado**    | **Implementação escalonada de todas as medidas**                | **🎯 35–50%**        | **Variável**    | **12-18 meses** |

### 🚀 Roadmap de Implementação

**Fase 1 - Quick Wins (1-3 meses):**
1. ✅ Auditoria imediata de motoristas críticos
2. 📸 Implementação de validação com foto
3. 📊 Dashboard de monitoramento em tempo real

**Fase 2 - Melhorias Técnicas (3-6 meses):**
1. 🔐 Sistema de QR Code dinâmico
2. 📈 Algoritmos de scoring de risco
3. 🗺️ Monitoramento geotemporal

**Fase 3 - Inovação Avançada (6-12 meses):**
1. 🤖 IA para detecção preditiva
2. 🔄 Sistema de feedback contínuo
3. 📊 Analytics avançado com BigData

---

## 📊 Resultados e Métricas de Sucesso

### 📈 KPIs de Acompanhamento

**Métricas Primárias:**
- 🎯 **Taxa geral de fraude:** Baseline 4.8% → Meta 2.4% (50% redução)
- 💰 **Valor recuperado:** $150K/mês estimado
- ⏱️ **Tempo de investigação:** 5 dias → 1 dia (80% redução)

**Métricas Secundárias:**
- 👥 **Satisfação do cliente:** Aumento de 15%
- 🚚 **Eficiência de entrega:** Melhoria de 20%
- 💼 **Rotatividade de motoristas:** Redução de 25%

### 🔬 Validação Científica

**Testes Estatísticos Aplicados:**
- **Chi-quadrado:** Independência entre variáveis categóricas
- **ANOVA:** Diferenças significativas entre grupos
- **Teste t:** Comparação de médias antes/depois
- **Correlação de Pearson:** Força de associações lineares

**Confiabilidade dos Modelos:**
- **Isolation Forest:** 87% precisão, 12% falsos positivos
- **Random Forest:** 91% AUC-ROC, 89% acurácia
- **K-Means:** Silhouette Score 0.73

---

## 🔧 Propostas de Aprimoramento Futuro

### 🧪 1. Experimentação Controlada (Testes A/B)
**Testes A/B Planejados:**
- 🆚 **QR Code dinâmico vs PIN tradicional** como método de autenticação (4 semanas)
- 📸 **Validação com foto vs sem validação** (6 semanas)
- 🤖 **IA vs regras tradicionais** (8 semanas)

**Métricas de Sucesso:**
- Taxa de fraude, satisfação do cliente, tempo de entrega

### 📦 2. Enriquecimento de Dados (Melhoria nos Dados)
**Novas Variáveis Propostas:**
- ✅ Adição de `gps_lat` e `gps_long` na entrega
- ✅ Registro do `delivery_timestamp` preciso
- ✅ Inclusão de `assinatura_cliente`, `foto_comprovante_url` e `cliente_feedback`

```sql
ALTER TABLE orders ADD COLUMN gps_lat DECIMAL(10,8);
ALTER TABLE orders ADD COLUMN gps_long DECIMAL(11,8);
ALTER TABLE orders ADD COLUMN delivery_timestamp DATETIME;
ALTER TABLE orders ADD COLUMN cliente_feedback TEXT;
ALTER TABLE orders ADD COLUMN foto_comprovante_url VARCHAR(255);
ALTER TABLE orders ADD COLUMN assinatura_digital BLOB;
```

### 🗣️ 3. Pesquisas Qualitativas
**Entrevistas Estruturadas:**
- 👨‍💼 **Entrevistas com motoristas** sobre desafios logísticos (n=50)
- 👥 **Coleta de feedback de clientes** em áreas com alta incidência de problemas (n=100)
- 🏢 **Gestores** (n=20): Processos internos e limitações

### 🤖 4. IA Avançada e Big Data
**Tecnologias Emergentes:**
- **Computer Vision** para análise automática de fotos
- **NLP** para análise de feedback textual
- **Graph Neural Networks** para detecção de redes fraudulentas
- **Real-time streaming** com Apache Kafka
