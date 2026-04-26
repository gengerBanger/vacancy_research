import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

def get_pie_plot(data, name):
    viridis_colors = px.colors.sample_colorscale('Viridis', np.linspace(0, 1, len(data)))

    pie = px.pie(
        values=data.values,
        names=data.index,
        title=name,
        color_discrete_sequence=viridis_colors
    )

    pie.update_traces(
        textposition='outside',
        textinfo='percent+label'
    )

    pie.update_layout(
        showlegend=False,
        title_font_size=24,
        title_font_family="Arial"
    )

    return pie


def get_bar_by_count(data, name):

    fig = px.bar(
            x=data.values,
            y=data.index,
            orientation='h',
            color=data.values,
            color_continuous_scale='Viridis'
        )
        
        # Настройка подписей осей и отображения
    fig.update_layout(
        title_text=name,
        title_font_size=24,
        title_font_family="Arial",
        height=max(400, len(data) * 20),  # Динамическая высота
        showlegend=False,
        xaxis_title="Количество вакансий",
        yaxis_title=None,
        font=dict(size=12),
        margin=dict(l=10, r=10, t=40, b=10),  # Отступы
        coloraxis_showscale=False
    )
    
    # Настройка отображения меток на осях
    fig.update_xaxes(
        tickformat="d",  # Целые числа
        gridcolor='lightgray',
        gridwidth=0.5
    )
    fig.update_yaxes(
        tickfont=dict(size=14),  # Размер шрифта для названий профессий
        automargin=True  # Автоматический отступ для длинных названий
    )

    return fig


def get_hitmap(data, name):
    vacancy_categories = data[data.str.len() == 2]

    # Превращаем каждую в отсортированную пару
    pairs = [tuple(sorted(cats)) for cats in vacancy_categories]

    # Считаем частоты
    pair_counts = Counter(pairs)

    # Все уникальные категории
    unique_cats = sorted(set(cat for pair in pair_counts for cat in pair))

    # Матрица со-встречаемости
    cooc = pd.DataFrame(0, index=unique_cats, columns=unique_cats, dtype=int)

    for (a, b), count in pair_counts.items():
        cooc.loc[a, b] = count
        cooc.loc[b, a] = count

    # Тепловая карта Plotly
    fig = go.Figure(data=go.Heatmap(
        z=cooc.values,
        x=cooc.columns,
        y=cooc.index,
        colorscale='Viridis',
        text=cooc.values,
        texttemplate='%{text}',
        hovertemplate='%{y} — %{x}<br>Вакансий: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title_text=name,
        title_font_size=24,
        title_font_family="Arial",
        xaxis_title=None,
        yaxis_title=None,
        xaxis_tickangle=-15,
        height=700
    )

    fig.update_yaxes(autorange='reversed')

    return fig


def get_multibar_plot(data, name, column, label_name):

    data = data.groupby(['category_by_name', column])['id'].nunique()
    viridis_colors = px.colors.sample_colorscale('Viridis', np.linspace(0, 1, 5))

    # Преобразуем в DataFrame
    df_plot = data.reset_index()
    df_plot.columns = ['category', column, 'count']

    # Сводная таблица
    pivot = df_plot.pivot(index='category', columns=column, values='count').fillna(0)

    # Нормализуем по строкам
    pivot_normalized = pivot.div(pivot.sum(axis=1), axis=0) * 100

    # Сортируем категории по убыванию самой большой доли (просто для красоты)
    pivot_normalized['max_dolya'] = pivot_normalized.max(axis=1)
    pivot_normalized = pivot_normalized.sort_values('max_dolya', ascending=False)
    pivot_normalized = pivot_normalized.drop('max_dolya', axis=1)

    # Переводим в long format
    df_melted = pivot_normalized.reset_index().melt(
        id_vars='category', 
        var_name=column, 
        value_name='percent'
    )

    # Сортируем внутри каждой категории по доле (от большей к меньшей)
    df_melted = df_melted.sort_values(['category', 'percent'], ascending=[True, False])

    df_melted = df_melted[df_melted['percent'] > 0]

    fig = px.bar(
        df_melted,
        x='category',
        y='percent',
        color=column,
        title=name,
        labels={'category': 'Категория', 'percent': 'Доля вакансий (%)', column: label_name},
        text='percent',
        barmode='stack',
        color_discrete_sequence=viridis_colors
    )

    fig.update_traces(texttemplate='%{text:.0f}%', textposition='inside')
    fig.update_layout(
        title_font_size=24,
        title_font_family="Arial",
        xaxis_tickangle=-45,
        height=600)

    return fig


def get_multibar_plot_by_spec(data, name, column, label_name):

    data = data.groupby(['spec_by_name', column])['id'].nunique()
    viridis_colors = px.colors.sample_colorscale('Viridis', np.linspace(0, 1, 5))

    # Преобразуем в DataFrame
    df_plot = data.reset_index()
    df_plot.columns = ['spec', column, 'count']

    # Сводная таблица
    pivot = df_plot.pivot(index='spec', columns=column, values='count').fillna(0)

    # Нормализуем по строкам
    pivot_normalized = pivot.div(pivot.sum(axis=1), axis=0) * 100

    # Сортируем категории по убыванию самой большой доли (просто для красоты)
    pivot_normalized['max_dolya'] = pivot_normalized.max(axis=1)
    pivot_normalized = pivot_normalized.sort_values('max_dolya', ascending=False)
    pivot_normalized = pivot_normalized.drop('max_dolya', axis=1)

    # Переводим в long format
    df_melted = pivot_normalized.reset_index().melt(
        id_vars='spec', 
        var_name=column, 
        value_name='percent'
    )

    # Сортируем внутри каждой категории по доле (от большей к меньшей)
    df_melted = df_melted.sort_values(['spec', 'percent'], ascending=[True, False])

    df_melted = df_melted[df_melted['percent'] > 0]

    fig = px.bar(
        df_melted,
        x='spec',
        y='percent',
        color=column,
        title=name,
        labels={'spec': 'Специализация', 'percent': 'Доля вакансий (%)', column: label_name},
        text='percent',
        barmode='stack',
        color_discrete_sequence=viridis_colors
    )

    fig.update_traces(texttemplate='%{text:.0f}%', textposition='inside')
    fig.update_layout(
        title_font_size=24,
        title_font_family="Arial",
        xaxis_tickangle=-45,
        height=600)

    return fig


def get_map(data, name, category='category_by_name', label='Категория'):

    df_map = data.dropna(subset=['address_lat', 'address_lng']).copy()

    fig = px.scatter_mapbox(
        df_map,
        lat='address_lat',
        lon='address_lng',
        color=category,
        hover_name=category,
        title=name,
        zoom=1,  # зум 1 = видно всю планету
        height=700,
        opacity=0.6,
        labels={category: label}
    )

    # Настройка стиля карты
    fig.update_layout(
        title_font_size=24,
        title_font_family="Arial",
        legend_title_font_size=18,  # размер заголовка
        legend_font_size=16,         # размер элементов
        mapbox_style="carto-positron",  
        mapbox_zoom=1,
        mapbox_center={"lat": 55, "lon": 60}  # центрируем на Россию/Евразию
    )

    return fig


def get_salary_plots(data, x='category_by_name', title='Средняя зарплата по категориям, опыту и типу выплат'):

    viridis_colors = px.colors.sample_colorscale('Viridis', np.linspace(0, 1, 4))

    fig = px.bar(
        data,
        x=x,
        y='mean_salary',
        color='experience',
        facet_row='salary_gross',
        title=title,
        labels={
            x: '',
            'mean_salary': 'Средняя зарплата (руб)',
            'experience': 'Опыт работы',
            'salary_gross': ''
        },
        barmode='group',
        text_auto='.0f',
        color_discrete_sequence=viridis_colors
    )

    fig.update_layout(
        title_font_size=24,
        title_font_family="Arial",
        height=950,
        xaxis_tickangle=-45,
        yaxis_tickformat=',d',
    )

    step = 50_000
    tick_vals = list(range(0, int(500_000) + step, step))
    tick_text = [f'{int(x/1000)}к' for x in tick_vals]  # 0к, 50к, 100к, 150к и т.д.

    fig.update_yaxes(
        tickvals=tick_vals,
        ticktext=tick_text,
        ticksuffix=' '
    )

    fig.update_traces(textfont_size=10, textposition='outside')

    return fig


def get_top_words(group, n=20):
    """Возвращает список кортежей вместо DataFrame"""
    all_words = []
    for words_list in group:
        unique_list = list(set(words_list))
        all_words.extend(unique_list)
    
    if not all_words:
        return []
    
    counter = Counter(all_words).most_common(n)
    total = len(group)
    
    # Возвращаем список кортежей
    return [(word, count, round((count/total)*100, 2)) for word, count in counter]