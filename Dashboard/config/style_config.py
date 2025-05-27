import streamlit as st

# Cores principais do tema
THEME = {
    'light': {
        'primary': '#296D84',
        'background': '#F9F9F9',
        'secondary_background': '#FFFCEE',
        'text': '#000000',
        'success': '#3CB371',
        'warning': '#FFA500',
        'danger': '#FF4500',
        'card_bg': '#FFFFFF',
        'card_shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'tooltip_bg': '#333333',
        'tooltip_text': '#FFFFFF',
        'chart_colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    },
    'dark': {
        'primary': '#68B5CE',
        'background': '#1E1E1E',
        'secondary_background': '#2D2D2D',
        'text': '#FFFFFF',
        'success': '#4CAF50',
        'warning': '#FFB74D',
        'danger': '#FF5252',
        'card_bg': '#333333',
        'card_shadow': '0 4px 6px rgba(0, 0, 0, 0.3)',
        'tooltip_bg': '#EEEEEE',
        'tooltip_text': '#000000',
        'chart_colors': ['#59a9e6', '#ffb07c', '#63d16f', '#ff7c7c', '#c59ced', '#c39183', '#ed9ed6', '#a5a5a5', '#dbdc7f', '#6ad7da']
    }
}

def apply_style():
    """Aplica as configurações de tema do Streamlit"""
    theme_mode = 'dark' if st.session_state.get('dark_mode', False) else 'light'
    
    st.markdown(f"""
        <style>
            /* REDUZIR TAMANHO DA SIDEBAR */
            .css-1d391kg {{
                width: 250px !important;
            }}
            
            .css-1lcbmhc {{
                width: 250px !important;
            }}
            
            .sidebar .sidebar-content {{
                width: 250px !important;
            }}
            
            /* Para versões mais recentes do Streamlit */
            section[data-testid="stSidebar"] {{
                width: 250px !important;
                min-width: 250px !important;
            }}
            
            section[data-testid="stSidebar"] > div {{
                width: 250px !important;
                min-width: 250px !important;
            }}
            
            /* Ajustar conteúdo principal para compensar */
            .main .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
                max-width: none;
            }}
            
            /* Reset alguns estilos padrão */
            div.block-container {{padding-top: 1rem;}}
            div.block-container {{max-width: 100%;}}
            
            /* Estilo para o cabeçalho fixo */
            .main-title {{
                color: {THEME[theme_mode]['primary']};
                text-align: center;
                margin: 0;
                padding: 0;
                font-size: 2rem;
            }}
            
            .sidebar-title {{
                color: {THEME[theme_mode]['primary']};
                font-size: 1.1rem;
                margin-bottom: 0.8rem;
            }}
            
            /* Reduzir padding e margin na sidebar */
            .sidebar .sidebar-content {{
                padding-top: 1rem;
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }}
            
            /* Ajustar fonte da sidebar para economizar espaço */
            .sidebar {{
                font-size: 0.9rem;
            }}
            
            .sidebar h1, .sidebar h2, .sidebar h3 {{
                margin-top: 0.5rem;
                margin-bottom: 0.5rem;
            }}
            
            .sidebar p {{
                margin-bottom: 0.5rem;
            }}
            
            /* Animações suaves */
            .stAnimatedContent {{
                transition: all 0.5s ease-in-out;
            }}
            
            /* Estilo específico para modo dark/light */
            body {{
                color: {THEME[theme_mode]['text']};
                background-color: {THEME[theme_mode]['background']};
            }}
            
            .reportview-container .markdown-text-container {{
                font-family: "sans serif";
            }}
            
            /* Estilos para os cards */
            .card {{
                border-radius: 0.5rem;
                background-color: {THEME[theme_mode]['card_bg']};
                box-shadow: {THEME[theme_mode]['card_shadow']};
                padding: 1rem;
                margin-bottom: 1rem;
                transition: transform 0.3s ease;
            }}
            
            .card:hover {{
                transform: translateY(-5px);
            }}
            
            /* Cores para KPIs */
            .success-metric {{
                color: {THEME[theme_mode]['success']};
                font-weight: bold;
            }}
            
            .warning-metric {{
                color: {THEME[theme_mode]['warning']};
                font-weight: bold;
            }}
            
            .danger-metric {{
                color: {THEME[theme_mode]['danger']};
                font-weight: bold;
            }}
            
            /* Tooltip personalizado */
            .tooltip {{
                position: relative;
                display: inline-block;
                cursor: help;
            }}
            
            .tooltip .tooltip-text {{
                visibility: hidden;
                width: 180px;
                background-color: {THEME[theme_mode]['tooltip_bg']};
                color: {THEME[theme_mode]['tooltip_text']};
                text-align: center;
                border-radius: 6px;
                padding: 5px;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -90px;
                opacity: 0;
                transition: opacity 0.3s;
                font-size: 0.8rem;
            }}
            
            .tooltip:hover .tooltip-text {{
                visibility: visible;
                opacity: 1;
            }}
            
            /* Melhorias de acessibilidade */
            button {{
                min-height: 44px;
            }}
            
            a:focus, button:focus, input:focus, select:focus {{
                outline: 2px solid {THEME[theme_mode]['primary']};
                outline-offset: 2px;
            }}
            
            /* Responsividade */
            @media (max-width: 1200px) {{
                section[data-testid="stSidebar"] {{
                    width: 220px !important;
                    min-width: 220px !important;
                }}
                
                section[data-testid="stSidebar"] > div {{
                    width: 220px !important;
                    min-width: 220px !important;
                }}
            }}
            
            @media (max-width: 768px) {{
                .main-title {{
                    font-size: 1.5rem;
                }}
                
                .card {{
                    padding: 0.75rem;
                }}
                
                section[data-testid="stSidebar"] {{
                    width: 200px !important;
                    min-width: 200px !important;
                }}
                
                section[data-testid="stSidebar"] > div {{
                    width: 200px !important;
                    min-width: 200px !important;
                }}
                
                .sidebar {{
                    font-size: 0.8rem;
                }}
            }}
        </style>
    """, unsafe_allow_html=True)

def get_custom_css():
    """Retorna CSS customizado para uso em partes específicas da aplicação"""
    theme_mode = 'dark' if st.session_state.get('dark_mode', False) else 'light'
    
    return f"""
    <style>
        /* Estilos para tabelas */
        .dataframe {{
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.9em;
            font-family: sans-serif;
            min-width: 400px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .dataframe thead tr {{
            background-color: {THEME[theme_mode]['primary']};
            color: #ffffff;
            text-align: left;
        }}
        
        .dataframe th,
        .dataframe td {{
            padding: 12px 15px;
        }}
        
        .dataframe tbody tr {{
            border-bottom: 1px solid #dddddd;
        }}
        
        .dataframe tbody tr:nth-of-type(even) {{
            background-color: {THEME[theme_mode]['secondary_background']};
        }}
        
        .dataframe tbody tr:last-of-type {{
            border-bottom: 2px solid {THEME[theme_mode]['primary']};
        }}
        
        /* Estilos para caixas de insights */
        .insight-box {{
            padding: 15px;
            background-color: {THEME[theme_mode]['secondary_background']};
            border-left: 4px solid {THEME[theme_mode]['primary']};
            margin-bottom: 15px;
            border-radius: 0 5px 5px 0;
        }}
        
        /* Ícones personalizados para insights */
        .icon-info:before {{
            content: 'ℹ️';
            margin-right: 10px;
        }}
        
        .icon-warning:before {{
            content: '⚠️';
            margin-right: 10px;
        }}
        
        .icon-alert:before {{
            content: '🚨';
            margin-right: 10px;
        }}
        
        /* Estilo para gráficos */
        .chart-container {{
            background-color: {THEME[theme_mode]['card_bg']};
            padding: 15px;
            border-radius: 10px;
            box-shadow: {THEME[theme_mode]['card_shadow']};
            margin-bottom: 20px;
        }}
        
        /* Estilo para KPIs */
        .kpi-container {{
            display: flex;
            flex-direction: column;
            padding: 15px;
            background-color: {THEME[theme_mode]['card_bg']};
            border-radius: 10px;
            box-shadow: {THEME[theme_mode]['card_shadow']};
            text-align: center;
            height: 100%;
        }}
        
        .kpi-title {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 10px;
            color: {THEME[theme_mode]['text']};
        }}
        
        .kpi-value {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .kpi-description {{
            font-size: 0.8rem;
            color: #666;
        }}
        
        /* Botões personalizados */
        .custom-button {{
            background-color: {THEME[theme_mode]['primary']};
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: background-color 0.3s;
            text-align: center;
            display: inline-block;
            margin: 5px;
        }}
        
        .custom-button:hover {{
            background-color: {THEME[theme_mode]['primary'] + '99'};
        }}
    </style>
    """

def create_tooltip(text, tooltip_text):
    """Cria um tooltip personalizado com informação contextual"""
    return f"""
    <span class="tooltip">{text}
        <span class="tooltip-text">{tooltip_text}</span>
    </span>
    """

def create_kpi_card(title, value, description="", color=""):
    """Cria um card de KPI com estilo personalizado"""
    color_class = ""
    if color == "success":
        color_class = "success-metric"
    elif color == "warning":
        color_class = "warning-metric"
    elif color == "danger":
        color_class = "danger-metric"
    
    return f"""
    <div class="kpi-container">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value {color_class}">{value}</div>
        <div class="kpi-description">{description}</div>
    </div>
    """

def create_insight_box(text, icon_type="info"):
    """Cria uma caixa de insight com ícone"""
    return f"""
    <div class="insight-box">
        <span class="icon-{icon_type}"></span>
        {text}
    </div>
    """