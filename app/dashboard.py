import streamlit as st
import pandas as pd

from utils import (get_bar_by_count, get_pie_plot, get_hitmap,
                    get_multibar_plot, get_map, get_salary_plots,
                    get_multibar_plot_by_spec, get_top_words)

# Настройка страницы
st.set_page_config(
    page_title="Анализ рынка вакансий",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомный CSS для красивого оформления
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .header-text {
        background: linear-gradient(120deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Загрузка данных
with st.spinner('Загрузка данных...'):
    df = pd.read_parquet('../research/dataset_for_dashboard.parquet')

tab1, tab2 = st.tabs(["Анализ по категориям", "Детальный анализ категорий и специализаций"])

with tab1:
    # Заголовок
    st.markdown('<div class="header-text">Аналитическая панель рынка IT вакансий</div>', unsafe_allow_html=True)

    # Верхние метрики
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df.id.nunique()}</div>
            <div class="metric-label">Вакансий</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        unique_spec = df.explode('spec_by_name')['spec_by_name'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_spec}</div>
            <div class="metric-label">Специальностей</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        unique_companies = df['employer_name'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_companies}</div>
            <div class="metric-label">Компаний</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        unique_city = df['address_city'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_city}</div>
            <div class="metric-label">Городов</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # КОЛИЧЕСТВО ВАКАНСИЙ ПО КАТЕГОРИЯМ И ПРОФЕССИЯМ

    # ПАЙПЛОТ ПО КАТЕГОРИЯМ

    pie_plot, table = st.columns(2)
    cat_counts = df.groupby('category_by_name')['id'].nunique()

    with pie_plot:
        
        st.plotly_chart(
            get_pie_plot(cat_counts, 'Распределение вакансий по категориям'),
            use_container_width=True
            )
        
    with table:
        for_table_df = cat_counts.reset_index()
        for_table_df.columns = ['Категория', 'Количество вакансий']
        for_table_df = for_table_df.sort_values('Количество вакансий', ascending=False)
        for_table_df.index = range(1, len(for_table_df) + 1)

        st.subheader("")

        st.dataframe(
            for_table_df,
            use_container_width=False
        )
    
    st.markdown("---")

    # СПЕЦИАЛИЗАЦИИ ПО КОЛИЧЕСТВУ ВАКАНСИЙ
    top_scep, tail_spec = st.columns(2)
    profession_counts = df.groupby('spec_by_name')['id'].nunique().sort_values(ascending=False)

    with top_scep:

        data = profession_counts.head(15).sort_values()
    
        st.plotly_chart(
            get_bar_by_count(data, 'Наиболее востребованные професии'),
            use_container_width=True
            )
    
    with tail_spec:

        data = profession_counts.tail(15).sort_values()
    
        st.plotly_chart(
            get_bar_by_count(data, 'Наименее востребованные професии'),
            use_container_width=True
            )
        
    st.markdown("---")   

    # Частота пар разных категорий в рамках одной вакансии   
    vacancy_categories = df.groupby('id')['category_by_name'].apply(set)

    st.plotly_chart(
        get_hitmap(vacancy_categories, 'Частота пар разных категорий в рамках одной вакансии'),
        use_container_width=True
        )
    
    st.markdown("---") 

    st.plotly_chart(
        get_multibar_plot(df,
                           'Доля форматов работы по категориям',
                           'schedule',
                           'Формат работы'),
        use_container_width=True
        )
    
    st.plotly_chart(
        get_multibar_plot(df,
                           'Доля требуемого опыта работы по категориям',
                           'experience',
                           'Опыт'),
        use_container_width=True
        )
    
    st.markdown("---") 

    grouped = df.groupby(['category_by_name', 'experience', 'salary_gross'])[['salary_from_rub', 'salary_to_rub']].mean()

    grouped['mean_salary'] = round((grouped['salary_from_rub'] + grouped['salary_to_rub']) / 2, 1)

    grouped = grouped.reset_index()

    st.plotly_chart(
        get_salary_plots(grouped),
        use_container_width=True
        )

    st.markdown("---") 

    st.plotly_chart(
        get_map(df, 'Распределение вакансий по миру'),
        use_container_width=True
        )
    

with tab2:
    # SIDEBAR - Фильтры
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/job.png", width=80)
        st.title("🔍 Фильтры")

        filtered_df = df.copy()
        category_df = df.copy()

        # Фильтр по категории 
        category_counts = filtered_df.groupby('category_by_name')['id'].nunique()
        categories = category_counts.sort_values(ascending=False).index.tolist()
        selected_category = st.selectbox("Выберите категорию", categories)
        
        filtered_df = filtered_df[filtered_df['category_by_name'] == selected_category]
        category_df = category_df[category_df['category_by_name'] == selected_category]

        # Фильтр по профессии
        profession_counts = filtered_df.groupby('spec_by_name')['id'].nunique()
        professions = ['Все'] + profession_counts.sort_values(ascending=False).index.tolist()
        selected_profession = st.selectbox("Выберите профессию", professions)
        if selected_profession != 'Все':
            filtered_df = filtered_df[filtered_df['spec_by_name'] == selected_profession]
        
        # Фильтр по городу
        cities_counts = filtered_df.groupby('address_city')['id'].nunique()
        cities = ['Все'] + cities_counts.sort_values(ascending=False).index.tolist()
        selected_city = st.selectbox("Выберите город", cities)
        if selected_city != 'Все':
            filtered_df = filtered_df[filtered_df['address_city'] == selected_city]
            category_df = category_df[category_df['address_city'] == selected_city]
        
        # Фильтр по опыту
        experience_filter = st.multiselect(
            "Опыт работы (лет)",
            options=sorted(filtered_df['experience'].unique()),
            default=sorted(filtered_df['experience'].unique())
        )
        filtered_df = filtered_df[filtered_df['experience'].isin(experience_filter)]
        category_df = category_df[category_df['experience'].isin(experience_filter)]

    # Проверка, есть ли данные после фильтрации
    if len(filtered_df) == 0:
        st.warning("Нет данных, соответствующих выбранным фильтрам. Измените параметры фильтрации.")
        st.stop()




    st.markdown(f'<div class="header-text">Аналитическая панель по категории {selected_category}</div>', unsafe_allow_html=True)

    # Верхние метрики
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{category_df.id.nunique()}</div>
            <div class="metric-label">Вакансий</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        unique_companies = category_df['employer_name'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_companies}</div>
            <div class="metric-label">Компаний</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        unique_city = category_df['address_city'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_city}</div>
            <div class="metric-label">Городов</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    pie_plot, table = st.columns(2)
    
    cat_counts = category_df.groupby('spec_by_name')['id'].nunique()

    with pie_plot:
        
        st.plotly_chart(
            get_pie_plot(cat_counts, 'Распределение специальностей в категории'),
            use_container_width=True
            )
        
    with table:
        for_table_df = cat_counts.reset_index()
        for_table_df.columns = ['Специализация', 'Количество вакансий']
        for_table_df = for_table_df.sort_values('Количество вакансий', ascending=False)
        for_table_df.index = range(1, len(for_table_df) + 1)

        st.subheader("")

        st.dataframe(
            for_table_df,
            use_container_width=False
        )
    
    st.markdown("---")

    st.plotly_chart(
        get_multibar_plot_by_spec(category_df,
                           'Доля требуемого опыта работы по специальностям',
                           'experience',
                           'Опыт'),
        use_container_width=True
        )
    
    st.markdown("---")

    grouped = category_df.groupby(['spec_by_name', 'experience', 'salary_gross'])[['salary_from_rub', 'salary_to_rub']].mean()

    grouped['mean_salary'] = round((grouped['salary_from_rub'] + grouped['salary_to_rub']) / 2, 1)

    grouped = grouped.reset_index()

    st.plotly_chart(
        get_salary_plots(grouped, 'spec_by_name', 'Средняя зарплата по специальностям, опыту и типу выплат'),
        use_container_width=True
        )

    st.markdown("---") 

    top_by_category = category_df.groupby('category_by_name', as_index=False)['latin_words'].apply(
        lambda x: get_top_words(x, 20)
    )
    top_by_category = top_by_category.explode('latin_words')
    top_by_category['Термин/Навык'] = top_by_category.latin_words.str[0]
    top_by_category['Количество вакансий со словом в категории'] = top_by_category.latin_words.str[1]
    top_by_category['Доля от общего количества вакансий в категории'] = top_by_category.latin_words.str[2]
    top_by_category.drop(['latin_words', 'category_by_name'], axis=1, inplace=True)
    top_by_category.index = range(1, len(for_table_df) + 1)

    st.subheader("Топ навыков по категории")

    st.dataframe(
            top_by_category,
            use_container_width=False
        )
    
    st.markdown("---")

    st.plotly_chart(
        get_map(category_df, 'Распределение вакансий по миру', 'spec_by_name', 'Специализация'),
        use_container_width=True
        )
    
    st.markdown("---")


    st.markdown(f'<div class="header-text">Аналитическая панель по профессии {selected_profession}</div>', unsafe_allow_html=True)

    # Верхние метрики
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{filtered_df.id.nunique()}</div>
            <div class="metric-label">Вакансий</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        unique_companies = filtered_df['employer_name'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_companies}</div>
            <div class="metric-label">Компаний</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        unique_city = filtered_df['address_city'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_city}</div>
            <div class="metric-label">Городов</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    top_by_spec= filtered_df.groupby('spec_by_name', as_index=False)['latin_words'].apply(
        lambda x: get_top_words(x, 20)
    )
    top_by_spec = top_by_spec.explode('latin_words')
    top_by_spec['Термин/Навык'] = top_by_spec.latin_words.str[0]
    top_by_spec['Количество вакансий со словом по специальности'] = top_by_spec.latin_words.str[1]
    top_by_spec['Доля от общего количества вакансий по специальности'] = top_by_spec.latin_words.str[2]
    top_by_spec.drop(['latin_words', 'spec_by_name'], axis=1, inplace=True)
    top_by_spec.index = range(1, len(for_table_df) + 1)

    st.subheader("Топ навыков по специальности")

    st.dataframe(
            top_by_spec,
            use_container_width=False
        )


# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>📊 Аналитическая панель создана с использованием Streamlit и Plotly</p>",
    unsafe_allow_html=True
)