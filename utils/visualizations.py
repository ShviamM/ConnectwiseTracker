import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_status_chart(df):
    """Create a pie chart of ticket statuses."""
    if 'Status' not in df.columns:
        return go.Figure()
    
    status_counts = df['Status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    fig = px.pie(
        status_counts,
        names='Status',
        values='Count',
        title='Ticket Status Distribution',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )
    
    fig.update_layout(
        legend_title_text='Status',
        showlegend=True
    )
    
    return fig

def create_priority_chart(df):
    """Create a pie chart of ticket priorities."""
    if 'Priority' not in df.columns:
        return go.Figure()
    
    # Define priority order
    priority_order = ['Low', 'Medium', 'High', 'Urgent']
    
    # Count priorities
    priority_counts = df['Priority'].value_counts().reset_index()
    priority_counts.columns = ['Priority', 'Count']
    
    # Set color scheme based on priority
    colors = {
        'Low': 'green',
        'Medium': 'yellow',
        'High': 'orange',
        'Urgent': 'red'
    }
    
    # Create color list based on priorities in the data
    color_list = [colors.get(p, 'gray') for p in priority_counts['Priority']]
    
    fig = px.pie(
        priority_counts,
        names='Priority',
        values='Count',
        title='Ticket Priority Distribution',
        color='Priority',
        color_discrete_map=colors
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value'
    )
    
    fig.update_layout(
        legend_title_text='Priority',
        showlegend=True
    )
    
    return fig

def create_age_histogram(df):
    """Create a histogram of ticket ages."""
    if 'Age' not in df.columns:
        return go.Figure()
    
    # Try to extract numeric values from Age column if not already done
    try:
        if df['Age'].dtype != 'float64' and df['Age'].dtype != 'int64':
            import re
            df['Age'] = df['Age'].astype(str).apply(
                lambda x: float(re.search(r'(\d+\.?\d*)', x).group(1))
                if re.search(r'(\d+\.?\d*)', x) else np.nan
            )
    except:
        pass
    
    # Remove NaN values
    df_age = df.dropna(subset=['Age'])
    
    # Create histogram bins
    if df_age.empty:
        return go.Figure()
    
    # Determine bin size based on data range
    age_max = df_age['Age'].max()
    
    if age_max <= 10:
        bin_size = 1
    elif age_max <= 30:
        bin_size = 2
    else:
        bin_size = 5
    
    fig = px.histogram(
        df_age,
        x='Age',
        nbins=int(age_max/bin_size) + 1,
        title='Ticket Age Distribution',
        labels={'Age': 'Age (Days)'},
        color_discrete_sequence=['rgba(0, 128, 255, 0.7)']
    )
    
    fig.update_layout(
        xaxis_title='Age (Days)',
        yaxis_title='Number of Tickets',
        bargap=0.1
    )
    
    return fig

def create_company_bar_chart(df):
    """Create a bar chart of tickets by company."""
    if 'Company' not in df.columns:
        return go.Figure()
    
    # Get top 10 companies by ticket count
    company_counts = df['Company'].value_counts().nlargest(10).reset_index()
    company_counts.columns = ['Company', 'Count']
    
    fig = px.bar(
        company_counts,
        x='Company',
        y='Count',
        title='Top 10 Companies by Ticket Count',
        labels={'Company': 'Company', 'Count': 'Number of Tickets'},
        color='Count',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title='Company',
        yaxis_title='Number of Tickets',
        xaxis={'categoryorder': 'total descending'}
    )
    
    # Rotate x-axis labels if there are many companies
    fig.update_layout(
        xaxis_tickangle=-45
    )
    
    return fig

def create_resource_allocation_chart(df):
    """Create a bar chart of tickets by resource."""
    if 'Resources' not in df.columns:
        return go.Figure()
    
    # Count tickets per resource
    resource_counts = df['Resources'].value_counts().nlargest(10).reset_index()
    resource_counts.columns = ['Resource', 'Count']
    
    # Replace empty resources with "Unassigned"
    resource_counts.loc[resource_counts['Resource'].isin(['', np.nan]), 'Resource'] = 'Unassigned'
    
    fig = px.bar(
        resource_counts,
        x='Resource',
        y='Count',
        title='Top 10 Resources by Ticket Count',
        labels={'Resource': 'Resource', 'Count': 'Number of Tickets'},
        color='Count',
        color_continuous_scale='Teal'
    )
    
    fig.update_layout(
        xaxis_title='Resource',
        yaxis_title='Number of Tickets',
        xaxis={'categoryorder': 'total descending'}
    )
    
    # Rotate x-axis labels
    fig.update_layout(
        xaxis_tickangle=-45
    )
    
    return fig

def create_ticket_trend_chart(df, time_period='daily'):
    """Create a line chart showing ticket count trends over time."""
    if 'Last Update' not in df.columns:
        return go.Figure()
    
    # Make a copy of the dataframe to avoid SettingWithCopyWarning
    df_trend = df.copy()
    
    # Ensure Last Update is datetime
    df_trend.loc[:, 'Last Update'] = pd.to_datetime(df_trend['Last Update'], errors='coerce')
    
    # Group by appropriate time period
    if time_period == 'daily':
        df_trend.loc[:, 'time_group'] = df_trend['Last Update'].dt.date
        x_title = 'Date'
    elif time_period == 'weekly':
        df_trend.loc[:, 'time_group'] = df_trend['Last Update'].dt.to_period('W').astype(str)
        x_title = 'Week'
    elif time_period == 'monthly':
        df_trend.loc[:, 'time_group'] = df_trend['Last Update'].dt.to_period('M').astype(str)
        x_title = 'Month'
    
    # Count tickets by time period
    ticket_counts = df_trend.groupby('time_group').size().reset_index(name='Count')
    
    # Convert time_group to string for plotting
    ticket_counts['time_group'] = ticket_counts['time_group'].astype(str)
    
    # Sort by time period
    ticket_counts = ticket_counts.sort_values('time_group')
    
    fig = px.line(
        ticket_counts,
        x='time_group',
        y='Count',
        title=f'Ticket Count by {time_period.capitalize()}',
        labels={'time_group': x_title, 'Count': 'Number of Tickets'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title='Number of Tickets'
    )
    
    # Add some styling to make it look better
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    # If there are many time periods, rotate the labels
    if len(ticket_counts) > 10:
        fig.update_layout(
            xaxis_tickangle=-45
        )
    
    return fig
