import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ================= 기본 데이터 =================
seismic_data = {
    'country': [
        '일본', '인도네시아', '필리핀', '칠레', '뉴질랜드',
        '미국', '멕시코', '페루', '터키', '이탈리아',
        '한국', '중국', '아르헨티나', '러시아'
    ],
    'magnitude': [
        6.2, 6.0, 5.8, 5.6, 5.4,
        4.5, 5.0, 5.3, 4.8, 4.6,
        3.5, 4.2, 4.5, 3.8
    ]
}

df = pd.DataFrame(seismic_data)

# ================= 취약성 데이터 =================
vulnerability = {
    '일본': 0.8, '인도네시아': 0.85, '필리핀': 0.8, '칠레': 0.75,
    '뉴질랜드': 0.7, '미국': 0.5, '멕시코': 0.6, '페루': 0.65,
    '터키': 0.55, '이탈리아': 0.45, '한국': 0.4,
    '중국': 0.5, '아르헨티나': 0.4, '러시아': 0.35
}

df['vulnerability'] = df['country'].map(vulnerability)

# ================= 진도 지수 계산 =================
df['impact'] = df['magnitude']

# ================= ISO-3 국가 코드 =================
iso_codes = {
    '일본': 'JPN', '인도네시아': 'IDN', '필리핀': 'PHL', '칠레': 'CHL',
    '뉴질랜드': 'NZL', '미국': 'USA', '멕시코': 'MEX', '페루': 'PER',
    '터키': 'TUR', '이탈리아': 'ITA', '한국': 'KOR', '중국': 'CHN',
    '아르헨티나': 'ARG', '러시아': 'RUS'
}

df['iso'] = df['country'].map(iso_codes)

# ================= 색상 스케일 =================
colorscale = [
    [0.0, '#ffffcc'],
    [0.25, '#ffeda0'],
    [0.5, '#feb24c'],
    [0.75, '#f03b20'],
    [1.0, '#bd0026']
]

# ================= 상위 3개 국가 =================
top3 = df.nlargest(3, 'impact')

# ================= 서브플롯 생성 =================
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        '지진 위험 기반 국가별 예상 진도 지수',
        '진도 vs 취약성 vs 진도 지수 (상위 10개국)',
        '상위 10개국 상세 분석',
        '진도별 국가 분포',
        '메트릭별 비교 (상위 5개국)',
        '진도 지수 상위 5개국 랭킹'
    ),
    specs=[
        [{'type': 'geo', 'rowspan': 2, 'colspan': 1}, {'type': 'scatter'}],
        [None, {'type': 'bar'}],
        [{'type': 'histogram'}, {'type': 'bar'}]
    ],
    vertical_spacing=0.12,
    horizontal_spacing=0.1,
    row_heights=[0.5, 0.25, 0.25]
)

# ================= 1. Choropleth 맵 =================
fig.add_trace(
    go.Choropleth(
        locations=df['iso'],
        z=df['impact'],
        colorscale=colorscale,
        colorbar=dict(
            title='<b>진도 지수</b>',
            thickness=15,
            len=0.5,
            x=0.48,
            y=0.65,
            yanchor='middle'
        ),
        marker_line_color='darkgray',
        marker_line_width=0.5,
        text=df['country'],
        hovertemplate='<b>%{text}</b><br>진도: %{customdata[0]:.1f}<br>취약성: %{customdata[1]:.2f}<br>진도 지수: %{z:.2f}<extra></extra>',
        customdata=df[['magnitude', 'vulnerability']].values,
        showscale=True
    ),
    row=1, col=1
)

# ================= 2. 산점도 =================
top10 = df.nlargest(10, 'impact')
fig.add_trace(
    go.Scatter(
        x=top10['magnitude'],
        y=top10['vulnerability'],
        mode='markers+text',
        marker=dict(
            size=top10['impact'] * 5,
            color=top10['impact'],
            colorscale='Reds',
            showscale=False,
            line=dict(width=1, color='darkred'),
            opacity=0.7
        ),
        text=top10['country'],
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>진도: %{x:.1f}<br>취약성: %{y:.2f}<extra></extra>',
        showlegend=False
    ),
    row=1, col=2
)

fig.update_xaxes(title_text='진도', row=1, col=2, showgrid=True, gridcolor='lightgray')
fig.update_yaxes(title_text='취약성', row=1, col=2, showgrid=True, gridcolor='lightgray')

# ================= 3. 상위 10개국 상세 분석 =================
fig.add_trace(
    go.Bar(
        x=top10['country'],
        y=top10['magnitude'],
        name='진도',
        marker_color='#3498db',
        hovertemplate='<b>%{x}</b><br>진도: %{y:.2f}<extra></extra>'
    ),
    row=2, col=2
)

fig.add_trace(
    go.Bar(
        x=top10['country'],
        y=top10['vulnerability'],
        name='취약성',
        marker_color='#e74c3c',
        hovertemplate='<b>%{x}</b><br>취약성: %{y:.2f}<extra></extra>'
    ),
    row=2, col=2
)

fig.update_xaxes(title_text='국가', row=2, col=2)
fig.update_yaxes(title_text='지수', row=2, col=2)

# ================= 4. 진도별 국가 분포 =================
magnitude_groups = {}
for _, row in df.iterrows():
    mag_range = f"{int(row['magnitude']*2)/2:.1f}"
    magnitude_groups.setdefault(mag_range, []).append(row['country'])

sorted_mags = sorted(magnitude_groups.keys(), key=float)
hover_texts = [
    f"진도: {mag}<br>국가: {', '.join(magnitude_groups[mag])}"
    for mag in sorted_mags
]

fig.add_trace(
    go.Bar(
        x=sorted_mags,
        y=[len(magnitude_groups[mag]) for mag in sorted_mags],
        marker_color='#f39c12',
        marker_line_color='#d68910',
        marker_line_width=1,
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts,
        showlegend=False
    ),
    row=3, col=1
)

fig.update_xaxes(title_text='진도 범위', row=3, col=1)
fig.update_yaxes(title_text='국가 수', row=3, col=1)

# ================= 5. 메트릭별 비교 =================
top5 = df.nlargest(5, 'impact')

fig.add_trace(
    go.Bar(
        x=top5['country'],
        y=top5['magnitude'],
        name='진도',
        marker_color='#3498db'
    ),
    row=3, col=2
)

fig.add_trace(
    go.Bar(
        x=top5['country'],
        y=top5['vulnerability'],
        name='취약성',
        marker_color='#e74c3c'
    ),
    row=3, col=2
)

fig.update_xaxes(title_text='국가', row=3, col=2)
fig.update_yaxes(title_text='지수', row=3, col=2)

# ================= 레이아웃 =================
fig.update_geos(
    showland=True,
    landcolor='rgb(243, 243, 243)',
    coastlinecolor='darkgray',
    coastlinewidth=1,
    projection_type='natural earth',
    showcoastlines=True,
    showframe=False,
    bgcolor='rgba(240, 248, 255, 0.5)',
    row=1, col=1
)

fig.update_layout(
    title=dict(
        text='<b>지진 위험 분석 대시보드</b>',
        font=dict(size=22),
        x=0.5,
        xanchor='center'
    ),
    height=1400,
    width=1400,
    margin=dict(l=60, r=60, t=100, b=80),
    font=dict(family='Arial, sans-serif', size=11),
    barmode='group',
    hovermode='closest',
    showlegend=True,
    legend=dict(
        x=0.5,
        y=-0.02,
        orientation='h',
        xanchor='center',
        yanchor='top'
    )
)

# ================= 주석 =================
annotation_text = '<br>'.join(
    [f"{i+1}. {row['country']} - {row['impact']:.2f}" for i, row in top3.iterrows()]
)

fig.add_annotation(
    x=0.02, y=0.95,
    xref='paper', yref='paper',
    text=f"<b>🔴 Top 3 영향국</b><br>{annotation_text}",
    showarrow=False,
    align='left',
    bgcolor='rgba(255, 255, 255, 0.95)',
    bordercolor='#bd0026',
    borderwidth=2,
    borderpad=10,
    font=dict(size=12)
)

fig.add_annotation(
    x=0.02, y=0.02,
    xref='paper', yref='paper',
    text='<i>진도 지수 = 진도 값 | 데이터: 지진학 통계 기반</i>',
    showarrow=False,
    align='left',
    bgcolor='rgba(255, 255, 255, 0.9)',
    bordercolor='gray',
    borderwidth=1,
    borderpad=8,
    font=dict(size=10, color='gray')
)

fig.show()
