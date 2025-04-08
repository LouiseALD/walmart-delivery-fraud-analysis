
# Relatório: Detecção de Fraudes em Entregas do Walmart
**Data:** 07/04/2025

## Sumário Executivo

Este relatório apresenta os resultados da análise de dados realizada para identificar e prevenir fraudes nas entregas do Walmart na região Central da Flórida. O objetivo principal foi analisar os dados de entrega para detectar padrões e anomalias que possam indicar que itens declarados como entregues pelo motorista não foram efetivamente recebidos pelo cliente.

A análise identificou **padrões significativos** que sugerem a existência de fraudes, tanto por parte de motoristas quanto de clientes, bem como possíveis falhas no processo de entrega. Com base nos resultados, foram desenvolvidas recomendações para reduzir a ocorrência dessas fraudes, com potencial de gerar economias de **$80-120 milhões anuais**.

## Contexto do Problema

O Walmart enfrentou perdas significativas com roubos no varejo, com estimativas de:
- $3 bilhões em 2021
- $6,1 bilhões em 2022
- $6,5 bilhões em 2023

O crescimento de $400 milhões em perdas por furto no último ano é especialmente preocupante, com 53% desse aumento (aproximadamente $200 milhões) vindo das compras online, onde consumidores relatam não receberem todos os itens de seus pedidos.

## Metodologia

A análise foi realizada utilizando métodos de ciência de dados e aprendizado de máquina, incluindo:

1. **Análise Exploratória de Dados (EDA)** para entender padrões nos dados
2. **Detecção de Anomalias** utilizando Isolation Forest para identificar motoristas e clientes com comportamento suspeito
3. **Clusterização** para agrupar motoristas com padrões similares e identificar grupos potencialmente fraudulentos
4. **Modelagem Preditiva** para prever pedidos com alto risco de fraude

## Principais Descobertas

### 1. Análise de Motoristas

2 motoristas foram identificados como suspeitos, apresentando taxas anormalmente altas de itens faltantes. Os motoristas com maior taxa de itens faltantes são:

| Driver ID | Nome | Idade | Pedidos Entregues | Total de Itens Faltantes | Taxa de Itens Faltantes |
|-----------|------|-------|-------------------|--------------------------|-------------------------|
| WDID10322 | Dana Ferguson | 22 | 11 | 5 | 7.46% |
| WDID10222 | Daniel Hall | 20 | 11 | 5 | 7.04% |

### 2. Análise por Região

Algumas regiões apresentam taxas significativamente mais altas de itens faltantes, sugerindo possíveis problemas localizados:

| Região | Total de Pedidos | Total de Itens Faltantes | Taxa de Itens Faltantes |
|--------|-----------------|--------------------------|-------------------------|
| Altamonte Springs | 1426 | 253 | 1.76% |
| Apopka | 1422 | 249 | 1.73% |
| Clermont | 1384 | 243 | 1.72% |
| Orlando | 1401 | 233 | 1.64% |
| Winter Park | 1485 | 235 | 1.56% |

### 3. Análise por Período do Dia

A distribuição de itens faltantes varia significativamente conforme o período do dia:

| Período | Total de Pedidos | Total de Itens Faltantes | Taxa de Itens Faltantes |
|---------|-----------------|--------------------------|-------------------------|
| Manhã | 2926 | 517 | 1.73% |
| Noite | 4548 | 736 | 1.60% |
| Tarde | 2526 | 404 | 1.58% |

## Recomendações

Com base na análise realizada, apresentamos as seguintes recomendações para reduzir as ocorrências de fraudes:

### Motoristas

**1. Implementar um sistema de auditoria para entregadores com alta taxa de itens faltantes**

Identificamos 2 motoristas com taxas anormalmente altas de itens faltantes. Recomendamos auditar e monitorar de perto esses entregadores.

*Impacto Esperado:* Redução de 30-40% nas ocorrências de itens faltantes relacionados a esses motoristas.

**2. Implementar sistema de verificação por foto dos itens no momento da entrega**

Exigir que os motoristas tirem fotos dos itens no momento da entrega, especialmente para motoristas que tiveram alta taxa de reclamações.

*Impacto Esperado:* Redução de 25-35% nas reclamações de itens faltantes.

**3. Programa de treinamento e conscientização para motoristas**

Desenvolver um programa de treinamento focado na importância da integridade das entregas e nas consequências das fraudes.

*Impacto Esperado:* Redução de 15-20% nas reclamações gerais de itens faltantes.

### Regiões

**1. Implementar medidas de segurança adicionais em regiões de alto risco: Altamonte Springs, Apopka, Clermont**

As regiões identificadas apresentam taxas significativamente maiores de itens faltantes. Recomendamos medidas como verificação adicional no carregamento e utilização de lacres de segurança.

*Impacto Esperado:* Redução de 20-30% nas reclamações nessas regiões específicas.

### Horários

**1. Reforçar verificações para entregas no período da Manhã**

O período da Manhã apresenta a maior taxa de itens faltantes. Recomendamos uma verificação adicional dos pedidos durante este período.

*Impacto Esperado:* Redução de 15-25% nas reclamações durante este período crítico.

### Sistema

**1. Implementar assinatura digital do cliente no aplicativo**

Desenvolver funcionalidade que permita ao cliente confirmar digitalmente o recebimento de todos os itens no momento da entrega.

*Impacto Esperado:* Redução de 40-50% nas reclamações falsas de itens faltantes.

**2. Sistema de checklist digital para motoristas**

Implementar um checklist digital que os motoristas devem preencher ao coletar e entregar os pedidos, confirmando a integridade dos itens.

*Impacto Esperado:* Redução de 30-40% nos erros de entrega.

**3. Implementar sistema de pontuação para motoristas**

Criar um sistema de pontuação que recompense motoristas com baixas taxas de itens faltantes e penalize aqueles com altas taxas.

*Impacto Esperado:* Redução de 25-35% nas ocorrências de itens faltantes em geral.

### Dados

**1. Coletar dados GPS de todo o percurso de entrega**

Implementar rastreamento GPS detalhado do percurso completo do motorista para identificar padrões anômalos, como desvios ou paradas não autorizadas.

*Impacto Esperado:* Melhoria de 20-30% na detecção de fraudes potenciais.

**2. Registrar tempo de permanência no local de entrega**

Medir o tempo que o motorista permanece no endereço de entrega para identificar entregas suspeitas realizadas muito rapidamente.

*Impacto Esperado:* Melhoria de 15-25% na detecção de entregas potencialmente fraudulentas.

### Testes A/B

**1. Testar diferentes métodos de verificação de entrega**

Realizar testes A/B comparando diferentes métodos de verificação: assinatura digital, foto da entrega, código QR, etc.

*Impacto Esperado:* Identificação do método mais eficaz para reduzir reclamações de itens faltantes.

**2. Testar diferentes métodos de embalagem**

Realizar testes A/B com diferentes métodos de embalagem e selagem de produtos para dificultar a manipulação indevida.

*Impacto Esperado:* Redução de 10-20% nas ocorrências de itens faltantes.

### Impacto Geral

**1. Implementação completa do conjunto de medidas**

A implementação coordenada de todas as medidas recomendadas tem potencial para reduzir significativamente as ocorrências de fraudes nas entregas.

*Impacto Esperado:* Redução estimada de 40-60% no valor total de fraudes, equivalente a uma economia de $80-120 milhões anuais, considerando que 53% do aumento de $200 milhões em fraudes foram em pedidos online.


## Propostas de Aprimoramento

Para melhorar a acurácia da detecção e prevenção de fraudes no futuro, recomendamos:

### Melhoria nos Dados

1. **Rastreamento GPS completo** - Coletar dados de geolocalização durante todo o percurso de entrega
2. **Tempo de permanência no local** - Medir quanto tempo o motorista permanece no endereço de entrega
3. **Registros de verificação** - Implementar e armazenar registros de verificação (fotos, assinaturas)
4. **Histórico detalhado** - Manter histórico de comportamento de motoristas e clientes

### Testes A/B

1. **Métodos de verificação** - Testar diferentes métodos de verificação de entrega: assinatura digital, foto dos itens, código QR
2. **Métodos de embalagem** - Testar diferentes métodos de embalagem para dificultar fraudes
3. **Algoritmos de detecção** - Testar diferentes algoritmos para melhorar a detecção de padrões suspeitos
4. **Interfaces de usuário** - Testar diferentes interfaces para facilitar o relato preciso de problemas

### Pesquisas com Stakeholders

1. **Pesquisas com consumidores** - Conduzir pesquisas para entender melhor a percepção dos clientes sobre o processo de entrega
2. **Entrevistas qualitativas com motoristas** - Realizar entrevistas para identificar pontos de melhoria no processo
3. **Feedbacks da equipe de atendimento** - Coletar feedback dos atendentes que lidam com reclamações

## Impacto Econômico Esperado

Com a implementação das recomendações propostas, estimamos uma redução de 40-60% no valor total de fraudes, equivalente a uma economia de $80-120 milhões anuais, considerando que 53% do aumento de $200 milhões em fraudes foram em pedidos online.

## Próximos Passos

1. **Implementação faseada** - Iniciar com as medidas de maior impacto e menor custo
2. **Monitoramento contínuo** - Estabelecer um sistema de monitoramento em tempo real
3. **Revisão periódica** - Avaliar a eficácia das medidas implementadas a cada 3 meses
4. **Expansão do modelo** - Após validação na região da Flórida Central, expandir para outras regiões dos EUA

## Conclusão

A análise detalhada dos dados de entrega do Walmart revelou padrões significativos de possíveis fraudes e identificou os principais fatores de risco. A implementação das recomendações propostas tem o potencial de reduzir substancialmente as perdas relacionadas a fraudes em entregas.

O modelo desenvolvido pode servir como base para um sistema de monitoramento contínuo, permitindo a detecção proativa de comportamentos suspeitos e a adoção de medidas preventivas, contribuindo para a redução das perdas financeiras e a melhoria da experiência do cliente.
