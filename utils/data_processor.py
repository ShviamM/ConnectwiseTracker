import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta

def clean_data(df):
    """
    Clean the Connectwise CSV data by removing image paths and converting data types.
    
    Args:
        df: DataFrame with the original Connectwise data
        
    Returns:
        DataFrame with cleaned data
    """
    # Make a copy to avoid modifying original data
    cleaned_df = df.copy()
    
    # Remove image paths from priority column
    if 'Priority' in cleaned_df.columns:
        # Extract color from image path
        cleaned_df['Priority'] = cleaned_df['Priority'].astype(str).apply(
            lambda x: extract_priority(x) if 'common/images' in x else x
        )
    
    # Clean image paths from Schedule column
    if 'Schedule' in cleaned_df.columns:
        # Extract schedule type from image path
        cleaned_df['Schedule'] = cleaned_df['Schedule'].astype(str).apply(
            lambda x: extract_schedule(x) if 'common/images' in x else x
        )
    
    # Convert Age to numeric if possible
    if 'Age' in cleaned_df.columns:
        # Try to extract numeric values from Age column
        cleaned_df['Age'] = cleaned_df['Age'].astype(str).apply(
            lambda x: extract_numeric(x)
        )
    
    # Clean SLA Status
    if 'SLA Status' in cleaned_df.columns:
        cleaned_df['SLA Status'] = cleaned_df['SLA Status'].astype(str).apply(
            lambda x: clean_sla_status(x)
        )
    
    # Convert date columns to datetime if they exist
    date_columns = ['Last Update', 'Due Date', 'Next Date']
    for col in date_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
    
    # Convert numeric columns
    numeric_columns = ['Total Hours', 'Budget']
    for col in numeric_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
    
    return cleaned_df

def extract_priority(priority_str):
    """Extract priority level from image path."""
    if 'lime.gif' in priority_str:
        return 'Low'
    elif 'yellow.gif' in priority_str:
        return 'Medium'
    elif 'orange.gif' in priority_str:
        return 'High'
    elif 'purple.gif' in priority_str:
        return 'Urgent'
    else:
        return priority_str

def extract_schedule(schedule_str):
    """Extract schedule type from image path."""
    if 'schedule-future.gif' in schedule_str:
        return 'Future'
    elif 'schedule-today.gif' in schedule_str:
        return 'Today'
    elif 'schedule-past.gif' in schedule_str:
        return 'Past'
    elif 'noperson.gif' in schedule_str:
        return 'Unassigned'
    else:
        return schedule_str

def extract_numeric(value_str):
    """Extract numeric values from string."""
    match = re.search(r'(\d+\.?\d*)', str(value_str))
    if match:
        return float(match.group(1))
    return np.nan

def clean_sla_status(sla_str):
    """Clean SLA status text."""
    # Remove timestamps and standardize
    if pd.isna(sla_str) or sla_str == 'nan':
        return 'No SLA'
    
    if 'Plan by' in sla_str:
        return 'Planned'
    elif 'Resolve by' in sla_str:
        return 'Needs Resolution'
    elif 'Waiting' in sla_str:
        return 'Waiting'
    else:
        return sla_str

def process_data(df, time_period='daily'):
    """
    Process the data for visualization based on the selected time period.
    
    Args:
        df: DataFrame with the cleaned Connectwise data
        time_period: The time period to aggregate by ('daily', 'weekly', or 'monthly')
    
    Returns:
        DataFrame with processed data for visualization
    """
    # Make a copy to avoid modifying original data
    processed_df = df.copy()
    
    # Ensure we have Last Update column for time-based analysis
    if 'Last Update' not in processed_df.columns:
        return processed_df
    
    # Create a safe version of the date column with default values for invalid dates
    has_valid_date = ~processed_df['Last Update'].isna()
    
    # For rows with invalid dates, use a default date to avoid losing data
    if has_valid_date.sum() < len(processed_df):
        # Fill missing dates with today's date to keep all rows
        default_date = pd.Timestamp('today')
        processed_df.loc[~has_valid_date, 'Last Update'] = default_date
    
    # Create date components - safely handle any remaining NaT values
    processed_df['date'] = processed_df['Last Update'].dt.date
    processed_df['day'] = processed_df['Last Update'].dt.day
    processed_df['week'] = processed_df['Last Update'].dt.isocalendar().week
    processed_df['month'] = processed_df['Last Update'].dt.month
    processed_df['year'] = processed_df['Last Update'].dt.year
    
    # Group by appropriate time period
    if time_period == 'daily':
        processed_df['time_group'] = processed_df['Last Update'].dt.date
    elif time_period == 'weekly':
        # Create a week-year combination
        processed_df['time_group'] = processed_df['year'].astype(str) + '-W' + processed_df['week'].astype(str).str.zfill(2)
    elif time_period == 'monthly':
        # Create a month-year combination
        processed_df['time_group'] = processed_df['year'].astype(str) + '-' + processed_df['month'].astype(str).str.zfill(2)
    
    return processed_df
