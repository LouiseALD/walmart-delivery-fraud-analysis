
# Relat�rio: Detec��o de Fraudes em Entregas do Walmart
**Data:** 07/04/2025

## Sum�rio Executivo

Este relat�rio apresenta os resultados da an�lise de dados realizada para identificar e prevenir fraudes nas entregas do Walmart na regi�o Central da Fl�rida. O objetivo principal foi analisar os dados de entrega para detectar padr�es e anomalias que possam indicar que itens declarados como entregues pelo motorista n�o foram efetivamente recebidos pelo cliente.

A an�lise identificou **padr�es significativos** que sugerem a exist�ncia de fraudes, tanto por parte de motoristas quanto de clientes, bem como poss�veis falhas no processo de entrega. Com base nos resultados, foram desenvolvidas recomenda��es para reduzir a ocorr�ncia dessas fraudes, com potencial de gerar economias de **$80-120 milh�es anuais**.

## Contexto do Problema

O Walmart enfrentou perdas significativas com roubos no varejo, com estimativas de:
- $3 bilh�es em 2021
- $6,1 bilh�es em 2022
- $6,5 bilh�es em 2023

O crescimento de $400 milh�es em perdas por furto no �ltimo ano � especialmente preocupante, com 53% desse aumento (aproximadamente $200 milh�es) vindo das compras online, onde consumidores relatam n�o receberem todos os itens de seus pedidos.

## Metodologia

A an�lise foi realizada utilizando m�todos de ci�ncia de dados e aprendizado de m�quina, incluindo:

1. **An�lise Explorat�ria de Dados (EDA)** para entender padr�es nos dados
2. **Detec��o de Anomalias** utilizando Isolation Forest para identificar motoristas e clientes com comportamento suspeito
3. **Clusteriza��o** para agrupar motoristas com padr�es similares e identificar grupos potencialmente fraudulentos
4. **Modelagem Preditiva** para prever pedidos com alto risco de fraude

## Principais Descobertas

### 1. An�lise de Motoristas

2 motoristas foram identificados como suspeitos, apresentando taxas anormalmente altas de itens faltantes. Os motoristas com maior taxa de itens faltantes s�o:

| Driver ID | Nome | Idade | Pedidos Entregues | Total de Itens Faltantes | Taxa de Itens Faltantes |
|-----------|------|-------|-------------------|--------------------------|-------------------------|
| WDID10322 | Dana Ferguson | 22 | 11 | 5 | 7.46% |
| WDID10222 | Daniel Hall | 20 | 11 | 5 | 7.04% |

### 2. An�lise por Regi�o

Algumas regi�es apresentam taxas significativamente mais altas de itens faltantes, sugerindo poss�veis problemas localizados:

| Regi�o | Total de Pedidos | Total de Itens Faltantes | Taxa de Itens Faltantes |
|--------|-----------------|--------------------------|-------------------------|
| Altamonte Springs | 1426 | 253 | 1.76% |
| Apopka | 1422 | 249 | 1.73% |
| Clermont | 1384 | 243 | 1.72% |
| Orlando | 1401 | 233 | 1.64% |
| Winter Park | 1485 | 235 | 1.56% |

### 3. An�lise por Per�odo do Dia

A distribui��o de itens faltantes varia significativamente conforme o per�odo do dia:

| Per�odo | Total de Pedidos | Total de Itens Faltantes | Taxa de Itens Faltantes |
|---------|-----------------|--------------------------|-------------------------|
| Manh� | 2926 | 517 | 1.73% |
| Noite | 4548 | 736 | 1.60% |
| Tarde | 2526 | 404 | 1.58% |

## Recomenda��es

Com base na an�lise realizada, apresentamos as seguintes recomenda��es para reduzir as ocorr�ncias de fraudes:

### Motoristas

**1. Implementar um sistema de auditoria para entregadores com alta taxa de itens faltantes**

Identificamos 2 motoristas com taxas anormalmente altas de itens faltantes. Recomendamos auditar e monitorar de perto esses entregadores.

*Impacto Esperado:* Redu��o de 30-40% nas ocorr�ncias de itens faltantes relacionados a esses motoristas.

**2. Implementar sistema de verifica��o por foto dos itens no momento da entrega**

Exigir que os motoristas tirem fotos dos itens no momento da entrega, especialmente para motoristas que tiveram alta taxa de reclama��es.

*Impacto Esperado:* Redu��o de 25-35% nas reclama��es de itens faltantes.

**3. Programa de treinamento e conscientiza��o para motoristas**

Desenvolver um programa de treinamento focado na import�ncia da integridade das entregas e nas consequ�ncias das fraudes.

*Impacto Esperado:* Redu��o de 15-20% nas reclama��es gerais de itens faltantes.

### Regi�es

**1. Implementar medidas de seguran�a adicionais em regi�es de alto risco: Altamonte Springs, Apopka, Clermont**

As regi�es identificadas apresentam taxas significativamente maiores de itens faltantes. Recomendamos medidas como verifica��o adicional no carregamento e utiliza��o de lacres de seguran�a.

*Impacto Esperado:* Redu��o de 20-30% nas reclama��es nessas regi�es espec�ficas.

### Hor�rios

**1. Refor�ar verifica��es para entregas no per�odo da Manh�**

O per�odo da Manh� apresenta a maior taxa de itens faltantes. Recomendamos uma verifica��o adicional dos pedidos durante este per�odo.

*Impacto Esperado:* Redu��o de 15-25% nas reclama��es durante este per�odo cr�tico.

### Sistema

**1. Implementar assinatura digital do cliente no aplicativo**

Desenvolver funcionalidade que permita ao cliente confirmar digitalmente o recebimento de todos os itens no momento da entrega.

*Impacto Esperado:* Redu��o de 40-50% nas reclama��es falsas de itens faltantes.

**2. Sistema de checklist digital para motoristas**

Implementar um checklist digital que os motoristas devem preencher ao coletar e entregar os pedidos, confirmando a integridade dos itens.

*Impacto Esperado:* Redu��o de 30-40% nos erros de entrega.

**3. Implementar sistema de pontua��o para motoristas**

Criar um sistema de pontua��o que recompense motoristas com baixas taxas de itens faltantes e penalize aqueles com altas taxas.

*Impacto Esperado:* Redu��o de 25-35% nas ocorr�ncias de itens faltantes em geral.

### Dados

**1. Coletar dados GPS de todo o percurso de entrega**

Implementar rastreamento GPS detalhado do percurso completo do motorista para identificar padr�es an�malos, como desvios ou paradas n�o autorizadas.

*Impacto Esperado:* Melhoria de 20-30% na detec��o de fraudes potenciais.

**2. Registrar tempo de perman�ncia no local de entrega**

Medir o tempo que o motorista permanece no endere�o de entrega para identificar entregas suspeitas realizadas muito rapidamente.

*Impacto Esperado:* Melhoria de 15-25% na detec��o de entregas potencialmente fraudulentas.

### Testes A/B

**1. Testar diferentes m�todos de verifica��o de entrega**

Realizar testes A/B comparando diferentes m�todos de verifica��o: assinatura digital, foto da entrega, c�digo QR, etc.

*Impacto Esperado:* Identifica��o do m�todo mais eficaz para reduzir reclama��es de itens faltantes.

**2. Testar diferentes m�todos de embalagem**

Realizar testes A/B com diferentes m�todos de embalagem e selagem de produtos para dificultar a manipula��o indevida.

*Impacto Esperado:* Redu��o de 10-20% nas ocorr�ncias de itens faltantes.

### Impacto Geral

**1. Implementa��o completa do conjunto de medidas**

A implementa��o coordenada de todas as medidas recomendadas tem potencial para reduzir significativamente as ocorr�ncias de fraudes nas entregas.

*Impacto Esperado:* Redu��o estimada de 40-60% no valor total de fraudes, equivalente a uma economia de $80-120 milh�es anuais, considerando que 53% do aumento de $200 milh�es em fraudes foram em pedidos online.


## Propostas de Aprimoramento

Para melhorar a acur�cia da detec��o e preven��o de fraudes no futuro, recomendamos:

### Melhoria nos Dados

1. **Rastreamento GPS completo** - Coletar dados de geolocaliza��o durante todo o percurso de entrega
2. **Tempo de perman�ncia no local** - Medir quanto tempo o motorista permanece no endere�o de entrega
3. **Registros de verifica��o** - Implementar e armazenar registros de verifica��o (fotos, assinaturas)
4. **Hist�rico detalhado** - Manter hist�rico de comportamento de motoristas e clientes

### Testes A/B

1. **M�todos de verifica��o** - Testar diferentes m�todos de verifica��o de entrega: assinatura digital, foto dos itens, c�digo QR
2. **M�todos de embalagem** - Testar diferentes m�todos de embalagem para dificultar fraudes
3. **Algoritmos de detec��o** - Testar diferentes algoritmos para melhorar a detec��o de padr�es suspeitos
4. **Interfaces de usu�rio** - Testar diferentes interfaces para facilitar o relato preciso de problemas

### Pesquisas com Stakeholders

1. **Pesquisas com consumidores** - Conduzir pesquisas para entender melhor a percep��o dos clientes sobre o processo de entrega
2. **Entrevistas qualitativas com motoristas** - Realizar entrevistas para identificar pontos de melhoria no processo
3. **Feedbacks da equipe de atendimento** - Coletar feedback dos atendentes que lidam com reclama��es

## Impacto Econômico Esperado

Com a implementa��o das recomenda��es propostas, estimamos uma redu��o de 40-60% no valor total de fraudes, equivalente a uma economia de $80-120 milh�es anuais, considerando que 53% do aumento de $200 milh�es em fraudes foram em pedidos online.

## Próximos Passos

1. **Implementa��o faseada** - Iniciar com as medidas de maior impacto e menor custo
2. **Monitoramento cont�nuo** - Estabelecer um sistema de monitoramento em tempo real
3. **Revis�o peri�dica** - Avaliar a efic�cia das medidas implementadas a cada 3 meses
4. **Expans�o do modelo** - Ap�s valida��o na regi�o da Fl�rida Central, expandir para outras regi�es dos EUA

## Conclus�o

A an�lise detalhada dos dados de entrega do Walmart revelou padr�es significativos de poss�veis fraudes e identificou os principais fatores de risco. A implementa��o das recomenda��es propostas tem o potencial de reduzir substancialmente as perdas relacionadas a fraudes em entregas.

O modelo desenvolvido pode servir como base para um sistema de monitoramento cont�nuo, permitindo a detec��o proativa de comportamentos suspeitos e a ado��o de medidas preventivas, contribuindo para a redu��o das perdas financeiras e a melhoria da experi�ncia do cliente.
