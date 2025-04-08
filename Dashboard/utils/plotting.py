import plotly.express as px

def grafico_fraudes_por_periodo(df):
    dados = df.groupby('periodo')[['itens_faltantes']].sum().reset_index()
    fig = px.bar(
        dados,
        x='periodo',
        y='itens_faltantes',
        color='periodo',
        title='Itens Faltantes por Período do Dia',
        labels={'itens_faltantes': 'Quantidade de Itens Faltantes', 'periodo': 'Período do Dia'}
    )
    fig.update_layout(xaxis_title="Período", yaxis_title="Itens Faltantes", showlegend=False)
    return fig
