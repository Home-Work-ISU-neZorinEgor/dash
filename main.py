from dash import Dash, html, dcc, callback, Output, Input
import dash_draggable
import plotly.express as px
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

style_dashboard = {
    "height": '100%',
    "width": '100%',
    "display": "flex",
    "flex-direction": "column",
    "flex-grow": "0"
}

default_countries = ["United Kingdom"]


def create_line_chart(selected_countries, measure="pop"):
    filtered_df = df[df.country.isin(selected_countries)]
    return px.line(filtered_df, x="year", y=measure, color="country", title="Показатели по годам")


line_chart_component = html.Div([
    html.Table([
        html.Tr([
            html.Td(html.Span("Активные страны"), style={"white-space": "nowrap"}),
            html.Td(dcc.Dropdown(df.country.unique(), default_countries, multi=True, id='dropdown-active-countries'),
                    style={"width": "100%"}),
        ]),
        html.Tr([
            html.Td(html.Span("Мера")),
            html.Td(dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], "pop", id='dropdown-measure', clearable=False)),
        ])
    ], style={"margin": "0rem 1rem"}),
    dcc.Graph(id='line-chart', figure=create_line_chart(default_countries), style=style_dashboard, responsive=True)
], style=style_dashboard, id="line-chart-component")


def create_bubble_chart(x="gdpPercap", y="lifeExp", size="pop", year_from=None, year_to=None):
    filtered_df = df
    if year_from and year_to:
        filtered_df = df[df.year.between(year_from, year_to)]
    latest_data = filtered_df.sort_values(["continent", "year"], ascending=False).drop_duplicates("country")
    if size == "lifeExp":
        size = latest_data.lifeExp
        size = size / size.max()
        size = size ** 6
    return px.scatter(latest_data, x=x, y=y, size=size, color="continent", hover_name="country", size_max=60,
                      hover_data=["year"])


bubble_chart_component = html.Div([
    html.Table([
        html.Tr([
            html.Td(html.Span("По оси X"), style={"white-space": "nowrap"}),
            html.Td(dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], "gdpPercap", id='bubble-x', clearable=False),
                    style={"width": "100%"})
        ]),
        html.Tr([
            html.Td(html.Span("По оси Y")),
            html.Td(dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], "lifeExp", id='bubble-y', clearable=False)),
        ]),
        html.Tr([
            html.Td(html.Span("Размер")),
            html.Td(dcc.Dropdown(["pop", "lifeExp", "gdpPercap"], "pop", id='bubble-size', clearable=False)),
        ]),
    ], style={"margin": "0rem 1rem"}),
    dcc.Graph(id='bubble-chart', figure=create_bubble_chart(), style=style_dashboard, responsive=True)
], style=style_dashboard, id="bubble-chart-component")


def create_top_population_chart(year_from=None, year_to=None):
    filtered_df = df
    if year_from and year_to:
        filtered_df = df[df.year.between(year_from, year_to)]
    latest_data = filtered_df.sort_values("year", ascending=False).drop_duplicates("country")
    top_countries = latest_data.sort_values("pop", ascending=False)[:15][::-1]
    return px.bar(top_countries, x="pop", y="country", title="Топ 15 стран по населению", hover_data=["year"])


top_population_chart_component = html.Div([
    dcc.Graph(id='top-population-chart', figure=create_top_population_chart(), style=style_dashboard, responsive=True)
], style=style_dashboard, id="top-population-chart-component")


def create_population_pie_chart(year_from=None, year_to=None):
    filtered_df = df
    if year_from and year_to:
        filtered_df = df[df.year.between(year_from, year_to)]
    latest_data = filtered_df.sort_values("year", ascending=False).drop_duplicates("country")
    return px.pie(latest_data, values="pop", names="continent", title="Население континентов", hole=.3)


population_pie_chart_component = html.Div([
    dcc.Graph(id='population-pie-chart', figure=create_population_pie_chart(), style=style_dashboard, responsive=True)
], style=style_dashboard, id="population-pie-chart-component")

app.layout = html.Div([
    html.H1(children='Сравнение стран', style={'textAlign': 'start'}),
    dash_draggable.ResponsiveGridLayout([
        line_chart_component, bubble_chart_component, top_population_chart_component, population_pie_chart_component
    ], clearSavedLayout=True, layouts={
        "lg": [
            {"i": "line-chart-component", "x": 0, "y": 0, "w": 12, "h": 10},
            {"i": "bubble-chart-component", "x": 0, "y": 10, "w": 12, "h": 10},
            {"i": "top-population-chart-component", "x": 0, "y": 20, "w": 6, "h": 10},
            {"i": "population-pie-chart-component", "x": 6, "y": 20, "w": 6, "h": 10}
        ]
    })
])


# Callback для обновления линейного графика
@callback(
    Output('line-chart', 'figure'),
    Input('dropdown-active-countries', 'value'),
    Input('dropdown-measure', 'value')
)
def update_line_chart(selected_countries, measure):
    return create_line_chart(selected_countries, measure)


# Вспомогательная функция для извлечения диапазона лет
def extract_year_range(arg):
    year_from = None
    year_to = None
    if arg:
        if 'xaxis.range[0]' in arg:
            year_from = arg['xaxis.range[0]']
        if 'xaxis.range[1]' in arg:
            year_to = arg['xaxis.range[1]']
    return year_from, year_to


# Callback для обновления пузырькового графика
@callback(
    Output('bubble-chart', 'figure'),
    Input('bubble-x', 'value'),
    Input('bubble-y', 'value'),
    Input('bubble-size', 'value'),
    Input('line-chart', 'relayoutData'),
)
def update_bubble_chart(x, y, size, line_chart_zoom):
    return create_bubble_chart(x, y, size, *extract_year_range(line_chart_zoom))


# Callback для обновления столбчатого графика топ стран по населению
@callback(
    Output('top-population-chart', 'figure'),
    Input('line-chart', 'relayoutData'),
)
def update_top_population_chart(line_chart_zoom):
    return create_top_population_chart(*extract_year_range(line_chart_zoom))


# Callback для обновления круговой диаграммы
@callback(
    Output('population-pie-chart', 'figure'),
    Input('line-chart', 'relayoutData'),
)
def update_population_pie_chart(line_chart_zoom):
    return create_population_pie_chart(*extract_year_range(line_chart_zoom))


if __name__ == '__main__':
    app.run_server(debug=True)

