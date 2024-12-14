import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Cargar el archivo de Excel
file_path = r'C:\Users\arash\Downloads\ia\AI_PROYECT\eventos.xlsx'
df = pd.read_excel(file_path, engine='openpyxl')

# Filtrar filas donde 'Nível' es 'Erro'
error_rows = df[df['Nível'] == 'Erro']

# Convertir las columnas de fecha y hora a datetime
error_rows['Data y hora'] = pd.to_datetime(error_rows['Data y hora'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')

# Inicializar la app Dash
app = dash.Dash(__name__)

# Crear la interfaz gráfica del dashboard
app.layout = html.Div(children=[
    html.H1('Dashboard de Errores del Computador', style={'text-align': 'center'}),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='graph-type',
                options=[
                    {'label': 'Frecuencia de Errores por Día', 'value': 'errors_by_day'},
                    {'label': 'Frecuencia de Errores por Hora del Día', 'value': 'errors_by_hour'},
                    {'label': 'Errores por Fuente', 'value': 'errors_by_source'},
                    {'label': 'Errores por Categoría de Tarea', 'value': 'errors_by_task'},
                    {'label': 'Correlación de Errores por Proceso y Evento', 'value': 'errors_by_process_event'}
                ],
                value='errors_by_day',  # Valor inicial
                style={'width': '50%'}
            )
        ], style={'width': '25%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='graph')
        ], style={'width': '70%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'align-items': 'center'}),
])

# Callback para actualizar las gráficas según la selección
@app.callback(
    Output('graph', 'figure'),
    Input('graph-type', 'value')
)
def update_graph(selected_graph):
    try:
        # Asegúrate de que 'Data y hora' esté en formato datetime
        error_rows['Data y hora'] = pd.to_datetime(error_rows['Data y hora'], errors='coerce')
        
        # Verificar si los datos están vacíos o no tienen fechas válidas
        if error_rows['Data y hora'].isnull().all():
            print("Error: No se pudieron parsear las fechas correctamente.")
            return None
        
        # Selección del gráfico según la opción
        if selected_graph == 'errors_by_day':
            # Conteo de errores por día
            error_counts = error_rows['Data y hora'].dt.date.value_counts().sort_index()

            # Crear gráfico de línea para mostrar la frecuencia de errores por día
            fig = px.line(
                x=error_counts.index, 
                y=error_counts.values,
                labels={'x': 'Fecha', 'y': 'Número de Errores'}, 
                title='Frecuencia de Errores por Día'
            )

        elif selected_graph == 'errors_by_hour':
            # Conteo de errores por hora
            error_counts = error_rows['Data y hora'].dt.hour.value_counts().sort_index()

            # Crear gráfico de barras para mostrar la frecuencia de errores por hora
            fig = px.bar(
                x=error_counts.index, 
                y=error_counts.values,
                labels={'x': 'Hora del Día', 'y': 'Número de Errores'},
                title='Frecuencia de Errores por Hora del Día'
            )

        elif selected_graph == 'errors_by_source':
            # Conteo de errores por fuente
            error_counts = error_rows['Fuente'].value_counts()

            # Crear gráfico de barras para mostrar la frecuencia de errores por fuente
            fig = px.bar(
                x=error_counts.index, 
                y=error_counts.values,
                labels={'x': 'Fuente', 'y': 'Número de Errores'},
                title='Errores por Fuente'
            )

        elif selected_graph == 'errors_by_task':
            # Conteo de errores por categoría de tarea
            error_counts = error_rows['Categoria da Tarea'].value_counts()

            # Crear gráfico de barras para mostrar la frecuencia de errores por tarea
            fig = px.bar(
                x=error_counts.index, 
                y=error_counts.values,
                labels={'x': 'Categoría de Tarea', 'y': 'Número de Errores'},
                title='Errores por Categoría de Tarea'
            )
        
        elif selected_graph == 'errors_by_process_event':
            # Conteo de errores por proceso y evento
            error_counts_by_process = error_rows.groupby('Identificación de procesos').size()
            error_counts_by_event = error_rows.groupby('Identificación de eventos').size()

            # Crear gráfico de dispersión para mostrar la correlación de errores por proceso y evento
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=error_counts_by_process.index, 
                y=error_counts_by_process.values,
                mode='markers',
                name='Errores por Proceso'
            ))

            fig.add_trace(go.Scatter(
                x=error_counts_by_event.index, 
                y=error_counts_by_event.values,
                mode='markers',
                name='Errores por Evento'
            ))

            fig.update_layout(
                title='Correlación de Errores por Proceso y Evento',
                xaxis_title='Identificación del Proceso / Evento',
                yaxis_title='Número de Errores',
                showlegend=True
            )

    except Exception as e:
        # Captura cualquier error y muestra un mensaje
        print(f"Error al crear el gráfico: {e}")
        return None
    
    # Retornar el gráfico creado
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)