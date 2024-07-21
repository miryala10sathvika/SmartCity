import pandas as pd
import plotly.graph_objs as go

# Load data from CSV
df = pd.read_csv('./crowdResults/crowd_stats_history.csv')

# Calculate time differences
first_timestamp = df.iloc[0]['Timestamp']
df['Time'] = (df['Timestamp'] - first_timestamp)

# Calculate requests per second (RPS)
df['FPS'] = df['Failures/s']


# Create plot for Requests per Second
fig_rps = go.Figure()
fig_rps.add_trace(go.Scatter(x=df['Time'], y=df['FPS'], mode='lines+markers', name='Failures/s'))
fig_rps.update_layout(title='Failures per Second over Time',
                      xaxis_title='Time (seconds)',
                      yaxis_title='Failures per Second',
                      template='plotly',
                      hovermode='x unified')

# Save Requests per Second plot as HTML
fig_rps.write_html('crowd_failures.html', auto_open=True)

