import pandas as pd
import plotly.graph_objs as go

# Load data from CSV
df = pd.read_csv('./crowdResults/crowd_stats_history.csv')

# Calculate time differences
first_timestamp = df.iloc[0]['Timestamp']
df['Time'] = (df['Timestamp'] - first_timestamp)

# Calculate requests per second (RPS)
df['RPS'] = df['Requests/s']

# Calculate average response time
df['Avg Response Time'] = df['Total Average Response Time']

# Create plot for Requests per Second
fig_rps = go.Figure()
fig_rps.add_trace(go.Scatter(x=df['Time'], y=df['RPS'], mode='lines+markers', name='Requests/s'))
fig_rps.update_layout(title='Requests per Second over Time',
                      xaxis_title='Time (seconds)',
                      yaxis_title='Requests per Second',
                      template='plotly',
                      hovermode='x unified')

# Save Requests per Second plot as HTML
fig_rps.write_html('crowd_requests.html', auto_open=True)

# Create plot for Average Response Time
fig_response = go.Figure()
fig_response.add_trace(go.Scatter(x=df['Time'], y=df['Avg Response Time'], mode='lines+markers', name='Average Response Time'))
fig_response.update_layout(title='Average Response Time over Time',
                           xaxis_title='Time (seconds)',
                           yaxis_title='Average Response Time (ms)',
                           template='plotly',
                           hovermode='x unified')

# Save Average Response Time plot as HTML
fig_response.write_html('crowd_response.html', auto_open=True)
