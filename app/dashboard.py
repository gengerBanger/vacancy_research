import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

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

# ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ
@st.cache_data
def generate_vacancy_data(n_vacancies=500):
    """Генерация реалистичных тестовых данных о вакансиях"""
    
    np.random.seed(42)
    random.seed(42)
    
    # Профессии и их характеристики
    professions = {
        'Python Developer': {
            'skills': ['Python', 'Django', 'PostgreSQL', 'REST API', 'Git'],
            'salary_range': (120000, 250000),
            'growth': 0.15  # 15% рост рынка
        },
        'Data Scientist': {
            'skills': ['Python', 'SQL', 'Machine Learning', 'Pandas', 'TensorFlow'],
            'salary_range': (150000, 300000),
            'growth': 0.25
        },
        'Java Developer': {
            'skills': ['Java', 'Spring Boot', 'Microservices', 'Kafka', 'Docker'],
            'salary_range': (130000, 260000),
            'growth': 0.10
        },
        'Frontend Developer': {
            'skills': ['JavaScript', 'React', 'HTML/CSS', 'TypeScript', 'Next.js'],
            'salary_range': (110000, 220000),
            'growth': 0.12
        },
        'DevOps Engineer': {
            'skills': ['Docker', 'Kubernetes', 'Jenkins', 'AWS', 'Terraform'],
            'salary_range': (160000, 320000),
            'growth': 0.20
        },
        'Product Manager': {
            'skills': ['Product Management', 'Agile', 'Analytics', 'Jira', 'Leadership'],
            'salary_range': (180000, 350000),
            'growth': 0.18
        },
        'Sales Manager': {
            'skills': ['B2B Sales', 'CRM', 'Negotiation', 'Cold Calling', 'Leadership'],
            'salary_range': (90000, 200000),
            'growth': 0.05
        },
        'Marketing Specialist': {
            'skills': ['SMM', 'Content Marketing', 'SEO', 'Google Analytics', 'Email Marketing'],
            'salary_range': (80000, 180000),
            'growth': 0.08
        },
        'UI/UX Designer': {
            'skills': ['Figma', 'Adobe XD', 'User Research', 'Prototyping', 'Sketch'],
            'salary_range': (100000, 210000),
            'growth': 0.14
        },
        'QA Engineer': {
            'skills': ['Manual Testing', 'Automation', 'Selenium', 'Jira', 'SQL'],
            'salary_range': (80000, 170000),
            'growth': 0.07
        }
    }
    
    # Генерация данных
    data = []
    companies = ['Яндекс', 'Google', 'Microsoft', 'Amazon', 'Facebook', 'Тинькофф', 'Сбер', 'Ozon', 'Wildberries', 'VK']
    cities = ['Москва', 'СПб', 'Новосибирск', 'Екатеринбург', 'Казань', 'Нижний Новгород']
    
    start_date = datetime(2023, 1, 1)
    
    for i in range(n_vacancies):
        profession = random.choice(list(professions.keys()))
        prof_data = professions[profession]
        
        # Генерация зарплаты с трендом роста
        base_salary = random.randint(*prof_data['salary_range'])
        experience = random.choice([1, 2, 3, 5, 8])
        salary = base_salary + experience * 5000
        
        # Генерация даты публикации (больше свежих вакансий)
        days_ago = np.random.exponential(scale=30)
        days_ago = min(days_ago, 180)
        publish_date = start_date + timedelta(days=int(days_ago))
        
        # Описание вакансии
        skills_str = ', '.join(random.sample(prof_data['skills'], k=random.randint(3, 5)))
        description = f"""
        {profession} в компанию {random.choice(companies)}.
        Требуемый опыт: {experience} лет.
        Необходимые навыки: {skills_str}.
        Условия: ДМС, гибкий график, удаленная работа.
        Обязанности: разработка и поддержка проектов, работа в команде.
        """
        
        data.append({
            'id': i,
            'profession': profession,
            'company': random.choice(companies),
            'city': random.choice(cities),
            'salary': salary,
            'experience': experience,
            'publish_date': publish_date,
            'description': description.strip(),
            'skills_count': len(prof_data['skills']),
            'market_growth': prof_data['growth']
        })
    
    df = pd.DataFrame(data)
    
    # Добавляем кластеры на основе профессий
    profession_to_cluster = {prof: idx for idx, prof in enumerate(professions.keys())}
    df['cluster'] = df['profession'].map(profession_to_cluster)
    
    # Добавляем тренд (количество вакансий по месяцам)
    df['month'] = df['publish_date'].dt.to_period('M').astype(str)
    
    return df

# Загрузка данных
with st.spinner('Генерация данных...'):
    df = generate_vacancy_data(500)

# Заголовок
st.markdown('<div class="header-text">📊 Аналитическая панель рынка вакансий</div>', unsafe_allow_html=True)

# SIDEBAR - Фильтры
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/job.png", width=80)
    st.title("🔍 Фильтры")
    
    # Фильтр по профессии
    professions = ['Все'] + sorted(df['profession'].unique().tolist())
    selected_profession = st.selectbox("Выберите профессию", professions)
    
    # Фильтр по городу
    cities = ['Все'] + sorted(df['city'].unique().tolist())
    selected_city = st.selectbox("Выберите город", cities)
    
    # Фильтр по зарплате
    salary_range = st.slider(
        "Диапазон зарплаты (тыс. руб)",
        min_value=int(df['salary'].min()/1000),
        max_value=int(df['salary'].max()/1000),
        value=(50, 250)
    )
    
    # Фильтр по опыту
    experience_filter = st.multiselect(
        "Опыт работы (лет)",
        options=sorted(df['experience'].unique()),
        default=sorted(df['experience'].unique())
    )
    
    # Применение фильтров
    filtered_df = df.copy()
    if selected_profession != 'Все':
        filtered_df = filtered_df[filtered_df['profession'] == selected_profession]
    if selected_city != 'Все':
        filtered_df = filtered_df[filtered_df['city'] == selected_city]
    filtered_df = filtered_df[
        (filtered_df['salary'] >= salary_range[0]*1000) &
        (filtered_df['salary'] <= salary_range[1]*1000) &
        (filtered_df['experience'].isin(experience_filter))
    ]

# ОСНОВНОЙ КОНТЕНТ

# Верхние метрики
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(filtered_df)}</div>
        <div class="metric-label">Всего вакансий</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_salary = filtered_df['salary'].mean() if len(filtered_df) > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{int(avg_salary/1000)} тыс. ₽</div>
        <div class="metric-label">Средняя зарплата</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    unique_companies = filtered_df['company'].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{unique_companies}</div>
        <div class="metric-label">Компаний</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    top_city = filtered_df['city'].mode()[0] if len(filtered_df) > 0 else 'Нет'
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{top_city}</div>
        <div class="metric-label">Город-лидер</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Проверка, есть ли данные после фильтрации
if len(filtered_df) == 0:
    st.warning("Нет данных, соответствующих выбранным фильтрам. Измените параметры фильтрации.")
    st.stop()

# РЯД 1: Два графика
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Спрос на профессии")
    profession_counts = filtered_df['profession'].value_counts().head(8)
    fig1 = px.bar(
        x=profession_counts.values,
        y=profession_counts.index,
        orientation='h',
        color=profession_counts.values,
        color_continuous_scale='Viridis',
        title="Количество вакансий по профессиям"
    )
    fig1.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("💰 Зарплаты по профессиям")
    salary_by_prof = filtered_df.groupby('profession')['salary'].mean().sort_values(ascending=True).tail(8)
    fig2 = px.bar(
        x=salary_by_prof.values,
        y=salary_by_prof.index,
        orientation='h',
        color=salary_by_prof.values,
        color_continuous_scale='Hot',
        title="Средняя зарплата (тыс. руб)",
        labels={'x': 'Зарплата (руб)', 'y': 'Профессия'}
    )
    fig2.update_layout(height=400, showlegend=False)
    # Исправленная строка - применяем к объекту layout
    fig2.update_layout(xaxis_tickformat=',.0f')
    st.plotly_chart(fig2, use_container_width=True)

# РЯД 2: Тренды и распределение
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Динамика рынка")
    # Группировка по месяцам
    monthly_trend = filtered_df.groupby('month').size().reset_index(name='count')
    if len(monthly_trend) > 1:
        fig3 = px.line(
            monthly_trend,
            x='month',
            y='count',
            markers=True,
            title="Количество вакансий по месяцам",
            color_discrete_sequence=['#FF6B6B']
        )
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Недостаточно данных для отображения тренда")

with col2:
    st.subheader("🗺️ География вакансий")
    city_dist = filtered_df['city'].value_counts().head(6)
    fig4 = px.pie(
        values=city_dist.values,
        names=city_dist.index,
        title="Распределение по городам",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.3
    )
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

# РЯД 3: Опыт и компании
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Зависимость зарплаты от опыта")
    salary_by_exp = filtered_df.groupby('experience')['salary'].agg(['mean', 'min', 'max']).reset_index()
    fig5 = px.line(
        salary_by_exp,
        x='experience',
        y='mean',
        title="Зарплата в зависимости от опыта",
        labels={'experience': 'Опыт (лет)', 'mean': 'Средняя зарплата (руб)'},
        markers=True
    )
    # Добавляем доверительные интервалы
    fig5.add_scatter(
        x=salary_by_exp['experience'],
        y=salary_by_exp['min'],
        mode='lines',
        name='Минимум',
        line=dict(dash='dash', color='gray')
    )
    fig5.add_scatter(
        x=salary_by_exp['experience'],
        y=salary_by_exp['max'],
        mode='lines',
        name='Максимум',
        line=dict(dash='dash', color='gray')
    )
    fig5.update_layout(height=400)
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.subheader("🏢 Топ работодателей")
    company_counts = filtered_df['company'].value_counts().head(8)
    fig6 = px.bar(
        x=company_counts.values,
        y=company_counts.index,
        orientation='h',
        title="Количество вакансий по компаниям",
        color=company_counts.values,
        color_continuous_scale='Blues'
    )
    fig6.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig6, use_container_width=True)

# РЯД 4: Scatter plot и тепловая карта
st.subheader("🔬 Детальный анализ")

col1, col2 = st.columns(2)

with col1:
    # Scatter plot зарплата vs опыт
    fig7 = px.scatter(
        filtered_df,
        x='experience',
        y='salary',
        color='profession',
        size='skills_count',
        hover_data=['company', 'city'],
        title="Зарплата vs Опыт (размер = количество навыков)",
        labels={'experience': 'Опыт (лет)', 'salary': 'Зарплата (руб)'}
    )
    fig7.update_layout(height=500)
    st.plotly_chart(fig7, use_container_width=True)

with col2:
    # Тепловая карта (pivot table)
    heatmap_data = filtered_df.pivot_table(
        values='salary',
        index='profession',
        columns='city',
        aggfunc='mean'
    ).fillna(0)
    
    if not heatmap_data.empty and heatmap_data.shape[0] > 1 and heatmap_data.shape[1] > 1:
        fig8 = px.imshow(
            heatmap_data,
            text_auto='.0f',
            aspect='auto',
            title="Средняя зарплата по профессиям и городам (руб)",
            labels={'x': 'Город', 'y': 'Профессия', 'color': 'Зарплата'},
            color_continuous_scale='RdYlGn'
        )
        fig8.update_layout(height=500)
        st.plotly_chart(fig8, use_container_width=True)
    else:
        st.info("Недостаточно данных для тепловой карты (нужно минимум 2 профессии и 2 города)")

# РЯД 5: Детальная таблица
st.subheader("📋 Список вакансий")
with st.expander("Показать/скрыть таблицу"):
    # Форматирование для отображения
    display_df = filtered_df.copy()
    display_df['salary'] = display_df['salary'].apply(lambda x: f"{int(x/1000)} тыс. ₽")
    display_df['publish_date'] = display_df['publish_date'].dt.strftime('%Y-%m-%d')
    display_df = display_df[['profession', 'company', 'city', 'salary', 'experience', 'publish_date', 'description']]
    display_df.columns = ['Профессия', 'Компания', 'Город', 'Зарплата', 'Опыт', 'Дата', 'Описание']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        column_config={
            "Описание": st.column_config.TextColumn(width="large"),
            "Зарплата": st.column_config.TextColumn(width="small"),
        }
    )

# Дополнительная статистика в сайдбаре
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Статистика")
    
    if len(filtered_df) > 0:
        # Самые востребованные навыки
        all_skills = []
        for desc in filtered_df['description'].head(100):
            if 'Навыки:' in desc:
                skills_part = desc.split('Навыки:')[1].split('.')[0] if 'Навыки:' in desc else ''
                all_skills.extend([s.strip() for s in skills_part.split(',')])
        
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts().head(10)
            st.markdown("**Топ-10 навыков:**")
            for skill, count in skill_counts.items():
                st.progress(count / skill_counts.max(), text=f"{skill}: {count}")
    
    # Скачивание данных
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Скачать данные (CSV)",
        data=csv,
        file_name="vacancies_analysis.csv",
        mime="text/csv",
    )

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>📊 Аналитическая панель создана с использованием Streamlit и Plotly</p>",
    unsafe_allow_html=True
)