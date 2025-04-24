import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import re
import time
import base64
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from utils.data_processor import clean_data, process_data
from utils.visualizations import (
    create_status_chart, 
    create_priority_chart, 
    create_age_histogram, 
    create_company_bar_chart,
    create_resource_allocation_chart,
    create_ticket_trend_chart
)

# Set page configuration
st.set_page_config(
    page_title="NOC Tickets Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for customer-centric, eye-catching styling
st.markdown("""
<style>
    /* Main dashboard styling */
    .main-header {
        font-size: 42px !important;
        font-weight: 700 !important;
        color: #1E3A8A !important;
        text-align: center;
        padding: 15px 0;
        margin-bottom: 25px;
        background: linear-gradient(135deg, #1E3A8A, #3B82F6, #60A5FA);
        color: white !important;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.3);
    }
    
    .dashboard-subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 35px;
        color: #475569;
        line-height: 1.5;
    }
    
    .subheader {
        font-size: 28px !important;
        font-weight: 600 !important;
        color: #1E3A8A !important;
        padding: 8px 0;
        margin: 25px 0 20px 0;
        border-bottom: 3px solid #C7D2FE;
        position: relative;
    }
    
    .subheader::after {
        content: "";
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 80px;
        height: 3px;
        background-color: #3B82F6;
    }
    
    /* Enhanced metrics styling */
    .metric-container {
        background: linear-gradient(to right, #F9FAFB, #F3F4F6);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
        border-left: 6px solid #3B82F6;
        margin-bottom: 30px;
    }
    
    .stMetric {
        background-color: white !important;
        border-radius: 8px !important;
        padding: 15px !important;
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.08) !important;
        transition: transform 0.2s;
    }
    
    .stMetric:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Section headers and container styling */
    .row-header {
        font-weight: 600;
        font-size: 20px;
        margin-bottom: 15px;
        color: #1E40AF;
        display: inline-block;
        padding-bottom: 5px;
        border-bottom: 2px solid #C7D2FE;
    }
    
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.06);
        margin-bottom: 25px;
        border-top: 4px solid #3B82F6;
    }
    
    .info-container {
        background-color: #EFF6FF;
        border-radius: 8px;
        padding: 15px;
        margin: 20px 0;
        border-left: 5px solid #3B82F6;
        color: #1E3A8A;
    }
    
    /* Table and dataframe styling */
    div[data-testid="stDataFrame"] {
        border-radius: 10px !important;
        padding: 10px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid #E5E7EB;
    }
    
    .table-container {
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        overflow: hidden;
        margin-bottom: 30px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
    }
    
    th {
        background-color: #EFF6FF;
        padding: 10px;
        text-align: left;
        font-weight: 600;
        color: #1E3A8A;
        border-bottom: 2px solid #C7D2FE;
    }
    
    td {
        padding: 10px;
        border-bottom: 1px solid #E5E7EB;
    }
    
    tr:hover {
        background-color: #F9FAFB;
    }
    
    /* Priority color coding with improved styling */
    .priority-urgent {
        background-color: #EF4444 !important;
        color: white !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
    }
    
    .priority-high {
        background-color: #F59E0B !important;
        color: white !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
    }
    
    .priority-medium {
        background-color: #FBBF24 !important;
        color: #1F2937 !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(251, 191, 36, 0.3);
    }
    
    .priority-low {
        background-color: #10B981 !important;
        color: white !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    
    /* Status label styling */
    .status-open {
        background-color: #3B82F6;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    
    .status-closed {
        background-color: #10B981;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    
    .status-waiting {
        background-color: #F59E0B;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    
    /* Download button styling with animation */
    div.stDownloadButton > button {
        background: linear-gradient(135deg, #1E40AF, #3B82F6) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 24px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    div.stDownloadButton > button:hover {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6) !important;
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    div.stDownloadButton > button:active {
        transform: translateY(1px) !important;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.4) !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E5E7EB !important;
    }
    
    section[data-testid="stSidebar"] > div {
        padding: 2rem 1rem;
    }
    
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stDateInput label {
        color: #1E3A8A !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] h2 {
        color: #1E3A8A !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        margin-bottom: 1rem !important;
        border-bottom: 2px solid #C7D2FE;
        padding-bottom: 0.5rem;
    }
    
    /* Responsive fixes */
    @media (max-width: 768px) {
        .main-header {
            font-size: 32px !important;
            padding: 10px 0;
        }
        
        .subheader {
            font-size: 24px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Application title with enhanced styling
st.markdown("<h1 class='main-header'>NOC Tickets Dashboard</h1>", unsafe_allow_html=True)

# Display the new logo in header
with open('attached_assets/idggKYNyFJ_logos.jpeg', 'rb') as f:
    logo_bytes = f.read()
import base64
logo_b64 = base64.b64encode(logo_bytes).decode()

st.markdown(f"""
<div style="position: absolute; top: 20px; right: 30px; z-index: 1000;">
    <img src="data:image/jpeg;base64,{logo_b64}" alt="Company Logo" style="width: 80px; height: auto;">
</div>
""", unsafe_allow_html=True)

# No dashboard timestamp as requested

# Sidebar for file upload and filters
with st.sidebar:
    st.header("Data Controls")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Connectwise CSV file", type=["csv"])
    
    # Initialize session state for data storage if not exists
    if 'data' not in st.session_state:
        st.session_state.data = None
        
    if 'date_min' not in st.session_state:
        st.session_state.date_min = None
        
    if 'date_max' not in st.session_state:
        st.session_state.date_max = None
        
    if 'uploaded' not in st.session_state:
        st.session_state.uploaded = False
    
    # Add a reset button to clear uploaded file data
    if st.session_state.data is not None and 'uploaded' in st.session_state and st.session_state.uploaded:
        if st.button("Reset to Sample Data"):
            # Clear uploaded file from session state
            st.session_state.data = None
            st.session_state.uploaded = False
            # Force refresh
            st.rerun()
    
    # Process uploaded file if available
    if uploaded_file is not None:
        try:
            # Read the uploaded file
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            
            # Display total count before any processing
            st.info(f"✅ Total tickets in uploaded CSV: {len(df)}")
            
            # Clean data
            df = clean_data(df)
            
            # Force all tickets to appear
            st.write(f"Displaying all {len(df)} tickets from uploaded file")
            
            # Add timestamp to ensure we're seeing fresh data
            st.write(f"Data last loaded: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Store processed data in session state
            st.session_state.data = df
            # Mark as uploaded in session state
            st.session_state.uploaded = True
            
            # Extract date range from data
            date_col = 'Last Update'
            if date_col in df.columns and not df[date_col].empty:
                # Convert to datetime if not already
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                
                # Filter out invalid dates
                valid_dates = df[date_col].dropna()
                
                if not valid_dates.empty:
                    st.session_state.date_min = valid_dates.min().date()
                    st.session_state.date_max = valid_dates.max().date()
            
            st.success("Uploaded file processed successfully!")
        except Exception as e:
            st.error(f"Error processing uploaded file: {str(e)}")
    # Load sample data if no file is uploaded and no data is loaded yet
    elif st.session_state.data is None:
        try:
            # Load sample tickets from the attached CSV file
            csv_path = "attached_assets/srboard.csv"
            
            # First, manually count lines to confirm we have 158 total lines (157 tickets + header)
            with open(csv_path, 'r') as f:
                total_lines = sum(1 for line in f)
            
            # Now read with pandas
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            
            # Display total count before any processing
            st.write(f"Total tickets in sample CSV: {len(df)} (should be 157)")
            
            # Clean data
            df = clean_data(df)
            
            # Force all 157 tickets to appear - this is critical!
            st.write(f"Displaying all {len(df)} tickets from sample file")
            
            # Add timestamp to ensure we're seeing fresh data
            st.write(f"Data last loaded: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Store processed data in session state
            st.session_state.data = df
            
            # Extract date range from data
            date_col = 'Last Update'
            if date_col in df.columns and not df[date_col].empty:
                # Convert to datetime if not already
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                
                # Filter out invalid dates
                valid_dates = df[date_col].dropna()
                
                if not valid_dates.empty:
                    st.session_state.date_min = valid_dates.min().date()
                    st.session_state.date_max = valid_dates.max().date()
            
            st.success("Sample file processed successfully!")
        except Exception as e:
            st.error(f"Error processing sample file: {str(e)}")
    
    # Date filters (only show if data is loaded) - with custom time periods
    if st.session_state.data is not None:
        st.subheader("Date Range")
        
        # Custom time period dropdown
        date_options = {
            "1 Day": 1,
            "2 Days": 2,
            "7 Days": 7,
            "15 Days": 15,
            "30 Days": 30,
            "All Time": 0  # 0 means all time
        }
        
        selected_date_range = st.selectbox(
            "Select Time Period",
            options=list(date_options.keys()),
            index=5  # Default to "All Time"
        )
        
        # Calculate date range based on selection
        days = date_options[selected_date_range]
        
        if days > 0:
            # Calculate date range
            date_max = datetime.now().date()
            date_min = date_max - timedelta(days=days)
        else:
            # All time - set very wide range
            date_min = datetime(2000, 1, 1).date()
            date_max = datetime(2030, 12, 31).date()
        
        # Store in session state
        st.session_state.date_min = date_min
        st.session_state.date_max = date_max
        
        # Display current range for reference (can be removed if not needed)
        st.write(f"Showing data from {date_min} to {date_max}")
        
        # Set default time period to "Daily" without showing selector
        time_period = "Daily"
        
        # Filter options
        st.subheader("Filters")
        
        # Get unique values for filters
        if st.session_state.data is not None:
            if 'Status' in st.session_state.data.columns:
                status_options = ['All'] + sorted(st.session_state.data['Status'].unique().tolist())
                selected_status = st.selectbox("Status", status_options)
            
            if 'Company' in st.session_state.data.columns:
                # Get top 10 companies by ticket count + 'All' option
                company_counts = st.session_state.data['Company'].value_counts().head(10).index.tolist()
                company_options = ['All'] + sorted(company_counts)
                selected_company = st.selectbox("Company", company_options)
            
            if 'Resources' in st.session_state.data.columns:
                # Get top 10 resources by ticket count + 'All' option
                resource_counts = st.session_state.data['Resources'].value_counts().head(10).index.tolist()
                resource_options = ['All'] + sorted(resource_counts)
                selected_resource = st.selectbox("Resource", resource_options)

# Main content area
if st.session_state.data is None:
    st.info("Please upload a Connectwise CSV file to begin.")
else:
    # Filter data based on date range and other filters
    df = st.session_state.data
    
    # Filter data by selected date range
    filtered_df = df.copy()
    
    # Convert dates and filter by date range if 'Last Update' column exists
    if 'Last Update' in filtered_df.columns:
        filtered_df['Last Update'] = pd.to_datetime(filtered_df['Last Update'], errors='coerce')
        
        # Apply date filter if time period is not "All Time"
        if date_options[selected_date_range] > 0:
            # Create date range filter - make sure we're comparing datetime.date objects
            filtered_df = filtered_df[
                (filtered_df['Last Update'].dt.date >= date_min) & 
                (filtered_df['Last Update'].dt.date <= date_max)
            ]
            st.sidebar.success(f"Showing {len(filtered_df)} tickets from the past {date_options[selected_date_range]} days.")
    
    # Apply additional filters
    if 'selected_status' in locals() and selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    
    if 'selected_company' in locals() and selected_company != 'All':
        filtered_df = filtered_df[filtered_df['Company'] == selected_company]
    
    if 'selected_resource' in locals() and selected_resource != 'All':
        filtered_df = filtered_df[filtered_df['Resources'] == selected_resource]
    
    # Create processed data for visualization
    processed_data = process_data(filtered_df, time_period.lower())
    
    # Display summary metrics with enhanced eye-catching styling
    st.markdown("<h2 class='subheader'>Summary Metrics</h2>", unsafe_allow_html=True)
    
    # Custom CSS for more eye-catching metrics cards
    st.markdown("""
    <style>
        /* Enhanced metrics styling with gradient backgrounds and animations */
        .metrics-container {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            flex: 1;
            min-width: 200px;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
        }
        
        .metric-total {
            background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
        }
        
        .metric-total::before {
            background: linear-gradient(90deg, #3B82F6, #1E40AF);
        }
        
        .metric-age {
            background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
        }
        
        .metric-age::before {
            background: linear-gradient(90deg, #10B981, #047857);
        }
        
        .metric-unassigned {
            background: linear-gradient(135deg, #FEF2F2, #FEE2E2);
        }
        
        .metric-unassigned::before {
            background: linear-gradient(90deg, #EF4444, #B91C1C);
        }
        
        .metric-sla {
            background: linear-gradient(135deg, #FFF7ED, #FFEDD5);
        }
        
        .metric-sla::before {
            background: linear-gradient(90deg, #F97316, #C2410C);
        }
        
        .metric-label {
            font-size: 16px;
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 10px;
        }
        
        .metric-value {
            font-size: 30px;
            font-weight: 700;
            margin: 10px 0;
        }
        
        .metric-total .metric-value {
            color: #1E40AF;
        }
        
        .metric-age .metric-value {
            color: #047857;
        }
        
        .metric-unassigned .metric-value {
            color: #B91C1C;
        }
        
        .metric-sla .metric-value {
            color: #C2410C;
        }
        
        .metric-delta {
            font-size: 14px;
            font-weight: 500;
            padding: 3px 8px;
            border-radius: 20px;
            display: inline-block;
        }
        
        .delta-positive {
            background-color: #ECFDF5;
            color: #047857;
        }
        
        .delta-negative {
            background-color: #FEF2F2;
            color: #B91C1C;
        }
        
        .metric-icon {
            position: absolute;
            top: 15px;
            right: 15px;
            opacity: 0.2;
            font-size: 28px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Get the metrics values
    total_tickets = len(filtered_df)
    
    # Average age of tickets
    avg_age = "N/A"
    if 'Age' in filtered_df.columns:
        try:
            # Extract numeric value from Age column
            filtered_df.loc[:, 'Age_Numeric'] = filtered_df['Age'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
            avg_age = f"{filtered_df['Age_Numeric'].mean():.1f}"
        except:
            pass
    
    # Unassigned tickets
    unassigned = 0
    unassigned_pct = "0%"
    if 'Resources' in filtered_df.columns:
        unassigned = filtered_df[filtered_df['Resources'].isna() | (filtered_df['Resources'] == '')].shape[0]
        if len(filtered_df) > 0:
            unassigned_pct = f"{unassigned/len(filtered_df)*100:.1f}%"
    
    # SLA issues
    overdue = 0
    overdue_pct = "0%"
    if 'SLA Status' in filtered_df.columns:
        overdue = filtered_df[filtered_df['SLA Status'].str.contains('late|overdue', case=False, na=False)].shape[0]
        if len(filtered_df) > 0:
            overdue_pct = f"{overdue/len(filtered_df)*100:.1f}%"
    
    # Create a more standard grid layout for metrics with eye-catching colors
    # Use Streamlit's built-in layout rather than custom HTML that could render incorrectly
    
    # Create a custom container for metrics header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #EFF6FF, #DBEAFE); 
                padding: 15px; 
                border-radius: 10px; 
                margin-bottom: 15px;
                border-left: 5px solid #3B82F6;
                text-align: center;">
        <h3 style="margin:0; color: #1E3A8A; font-size: 20px;">Key Performance Indicators</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Use Streamlit's columns and metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Enhanced styling for each metric
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #EFF6FF, #DBEAFE); 
                    padding: 15px; 
                    border-radius: 10px; 
                    text-align: center;
                    border-top: 4px solid #3B82F6;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 28px; font-weight: 700; color: #1E40AF; margin-bottom: 5px;">""" + str(total_tickets) + """</div>
            <div style="font-size: 16px; color: #4B5563; font-weight: 600;">Total Tickets</div>
            <div style="margin-top: 10px; font-size: 14px; color: #6B7280;">Active ticket count</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #F0FDF4, #DCFCE7); 
                    padding: 15px; 
                    border-radius: 10px; 
                    text-align: center;
                    border-top: 4px solid #10B981;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 28px; font-weight: 700; color: #047857; margin-bottom: 5px;">""" + str(avg_age) + """</div>
            <div style="font-size: 16px; color: #4B5563; font-weight: 600;">Average Age</div>
            <div style="margin-top: 10px; font-size: 14px; color: #6B7280;">Days in system</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FEF2F2, #FEE2E2); 
                    padding: 15px; 
                    border-radius: 10px; 
                    text-align: center;
                    border-top: 4px solid #EF4444;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 28px; font-weight: 700; color: #B91C1C; margin-bottom: 5px;">""" + str(unassigned) + """</div>
            <div style="font-size: 16px; color: #4B5563; font-weight: 600;">Unassigned Tickets</div>
            <div style="margin-top: 10px; font-size: 14px; color: #6B7280;"><span style="background-color: #FEE2E2; padding: 2px 6px; border-radius: 12px; color: #B91C1C; font-weight: 500;">""" + str(unassigned_pct) + """ of total</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FFF7ED, #FFEDD5); 
                    padding: 15px; 
                    border-radius: 10px; 
                    text-align: center;
                    border-top: 4px solid #F97316;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 28px; font-weight: 700; color: #C2410C; margin-bottom: 5px;">""" + str(overdue) + """</div>
            <div style="font-size: 16px; color: #4B5563; font-weight: 600;">SLA Issues</div>
            <div style="margin-top: 10px; font-size: 14px; color: #6B7280;"><span style="background-color: #FFEDD5; padding: 2px 6px; border-radius: 12px; color: #C2410C; font-weight: 500;">""" + str(overdue_pct) + """ of total</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Keep the standard metrics but hidden (for compatibility with the rest of the app)
    with st.container():
        st.markdown("<div style='display:none'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Total Tickets", value=total_tickets)
        
        with col2:
            st.metric(label="Average Age (Days)", value=avg_age)
        
        with col3:
            st.metric(label="Unassigned Tickets", value=unassigned)
        
        with col4:
            st.metric(label="SLA Issues", value=overdue)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Visualization section with enhanced styling
    st.markdown("<h2 class='subheader'>Ticket Analytics</h2>", unsafe_allow_html=True)
    
    # Add a brief explanation for executives
    st.markdown("""
    <div style='background-color: #EFF6FF; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #3B82F6;'>
        <p style='margin: 0; color: #1E3A8A;'>The following analytics provide a visual overview of ticket distribution by status, priority, age, and company. 
        These visualizations help identify patterns and areas that need attention.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two rows of visualizations with enhanced styling
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        # Ticket Status Chart with box styling
        st.markdown("<p class='row-header'>Ticket Status Distribution</p>", unsafe_allow_html=True)
        if 'Status' in filtered_df.columns:
            status_fig = create_status_chart(filtered_df)
            # Update layout for better styling
            status_fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
            )
            st.plotly_chart(status_fig, use_container_width=True)
        else:
            st.error("Status data not available in the uploaded file.")
    
    with row1_col2:
        # Ticket Priority Chart with box styling
        st.markdown("<p class='row-header'>Ticket Priority Breakdown</p>", unsafe_allow_html=True)
        if 'Priority' in filtered_df.columns:
            priority_fig = create_priority_chart(filtered_df)
            # Update layout for better styling
            priority_fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
            )
            st.plotly_chart(priority_fig, use_container_width=True)
        else:
            st.error("Priority data not available in the uploaded file.")
    
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        # Ticket Age Distribution with box styling
        st.markdown("<p class='row-header'>Ticket Age Distribution</p>", unsafe_allow_html=True)
        if 'Age' in filtered_df.columns:
            try:
                age_fig = create_age_histogram(filtered_df)
                # Update layout for better styling
                age_fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(family="Arial, sans-serif", size=12)
                )
                st.plotly_chart(age_fig, use_container_width=True)
            except:
                st.error("Could not process Age data.")
        else:
            st.error("Age data not available in the uploaded file.")
    
    with row2_col2:
        # Company Distribution with box styling
        st.markdown("<p class='row-header'>Company Distribution</p>", unsafe_allow_html=True)
        if 'Company' in filtered_df.columns:
            company_fig = create_company_bar_chart(filtered_df)
            # Update layout for better styling
            company_fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12)
            )
            st.plotly_chart(company_fig, use_container_width=True)
        else:
            st.error("Company data not available in the uploaded file.")

    # Time trend analysis with enhanced styling
    st.markdown("<h2 class='subheader'>Daily Ticket Trend</h2>", unsafe_allow_html=True)
    if 'Last Update' in filtered_df.columns:
        trend_fig = create_ticket_trend_chart(filtered_df, time_period.lower())
        # Update layout for better styling
        trend_fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12)
        )
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.error("Date data not available for trend analysis.")
    
    # Resource allocation section with enhanced styling
    st.markdown("<h2 class='subheader'>Resource Allocation</h2>", unsafe_allow_html=True)
    if 'Resources' in filtered_df.columns:
        resource_fig = create_resource_allocation_chart(filtered_df)
        # Update layout for better styling
        resource_fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12)
        )
        st.plotly_chart(resource_fig, use_container_width=True)
    else:
        st.error("Resource data not available in the uploaded file.")
    
    # Top 10 Oldest Tickets section with enhanced styling
    st.markdown("<h2 class='subheader'>Top 10 Oldest Tickets</h2>", unsafe_allow_html=True)
    if 'Age' in filtered_df.columns and 'Age_Numeric' in filtered_df.columns:
        # Sort by age and display top 10 oldest tickets
        oldest_tickets = filtered_df.sort_values('Age_Numeric', ascending=False).head(10)
        
        # Apply color coding to priority
        def highlight_priority(val):
            if 'Urgent' in val:
                return f"<span class='priority-urgent'>{val}</span>"
            elif 'High' in val:
                return f"<span class='priority-high'>{val}</span>"
            elif 'Medium' in val:
                return f"<span class='priority-medium'>{val}</span>"
            elif 'Low' in val:
                return f"<span class='priority-low'>{val}</span>"
            else:
                return val
        
        # Apply styling to the dataframe
        if 'Priority' in oldest_tickets.columns:
            oldest_tickets['Priority'] = oldest_tickets['Priority'].apply(highlight_priority)
            styled_oldest = oldest_tickets[['Ticket #', 'Priority', 'Age', 'Status', 'Company', 'Summary Description', 'Resources']]
        else:
            styled_oldest = oldest_tickets[['Ticket #', 'Age', 'Status', 'Company', 'Summary Description', 'Resources']]
        
        st.write(styled_oldest.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.error("Age data not available to show oldest tickets.")
    
    # Top 10 Alerts section with enhanced styling
    st.markdown("<h2 class='subheader'>Top 10 Alerts</h2>", unsafe_allow_html=True)
    if 'Summary Description' in filtered_df.columns:
        # Find alerts in ticket descriptions 
        alerts_mask = filtered_df['Summary Description'].str.contains('Alert|Warning|Critical|Urgent|Emergency|Endgame', case=False, na=False)
        alert_tickets = filtered_df[alerts_mask].head(10)
        
        if not alert_tickets.empty:
            # Apply color coding to priority
            if 'Priority' in alert_tickets.columns:
                alert_tickets['Priority'] = alert_tickets['Priority'].apply(highlight_priority)
                styled_alerts = alert_tickets[['Ticket #', 'Priority', 'Status', 'Company', 'Summary Description', 'Resources']]
            else:
                styled_alerts = alert_tickets[['Ticket #', 'Status', 'Company', 'Summary Description', 'Resources']]
                
            st.write(styled_alerts.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.info("No alert tickets found in the dataset.")
    else:
        st.error("Summary data not available to show alerts.")
    
    # Detailed data view with enhanced styling
    st.markdown("<h2 class='subheader'>Detailed Ticket Data</h2>", unsafe_allow_html=True)
    st.dataframe(
        filtered_df,
        hide_index=True,
        use_container_width=True
    )
    
    # Create enhanced PDF export function for comprehensive executive report with customizable branding
    def create_pdf(dataframe, company_name="COMPANY", brand_color=(41, 128, 185), logo_size=40, include_timestamp=True):
        # Create a custom PDF class to add header with logo and footer
        class PDF(FPDF):
            def __init__(self, company_name, brand_color, logo_size, include_timestamp):
                super().__init__()
                self.company_name = company_name
                self.brand_color = brand_color
                self.logo_size = logo_size
                self.include_timestamp = include_timestamp
            
            def header(self):
                # Use Base64 encoded image as logo
                # Read the Base64 string from file
                try:
                    with open('logo_base64.txt', 'r') as f:
                        logo_b64 = f.read()
                    
                    # Create a temporary file for the image
                    import tempfile
                    import os
                    import base64
                    
                    # Create temporary file
                    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpeg')
                    temp_filename = temp.name
                    
                    # Write decoded base64 image to the temporary file
                    with open(temp_filename, 'wb') as f:
                        f.write(base64.b64decode(logo_b64))
                    
                    # Add image to PDF with custom size
                    self.image(temp_filename, x=210-self.logo_size-10, y=8, w=self.logo_size)
                    
                    # Clean up the temporary file
                    os.unlink(temp_filename)
                    
                except Exception as e:
                    # Fallback to text-based logo if there's any error
                    # Draw logo background with custom brand color
                    self.set_fill_color(*self.brand_color)  # Use custom brand color
                    x_pos = 210-self.logo_size-10  # Right-aligned position
                    self.rect(x_pos, 8, self.logo_size, 18, style='F')
                    
                    # Add border - darker shade of brand color
                    darker_color = tuple(max(0, c-40) for c in self.brand_color)
                    self.set_draw_color(*darker_color)
                    self.set_line_width(0.5)
                    self.rect(x_pos, 8, self.logo_size, 18, style='D')
                    
                    # Add company name/text
                    self.set_font('Arial', 'B', 12)
                    self.set_text_color(255, 255, 255)  # White text
                    self.set_xy(x_pos, 13)
                    self.cell(self.logo_size, 8, self.company_name, 0, 0, 'C')
                
                # Add title with date in the format "Daily Insights Date, Month Year"
                current_date = datetime.now().strftime("%d, %B %Y")
                self.set_font('Arial', 'B', 15)
                self.set_text_color(*self.brand_color)  # Use custom brand color
                self.set_xy(10, 10)
                self.cell(0, 10, f'Daily Insights {current_date}', 0, 1, 'C')
                
                # Add generation timestamp based on user preference
                if self.include_timestamp:
                    self.set_font('Arial', 'I', 10)
                    self.set_text_color(100, 100, 100)
                    self.cell(0, 5, 'Executive Report', 0, 1, 'C')
                
                # Add a line
                self.set_draw_color(59, 130, 246)  # Blue line
                self.line(10, 25, 200, 25)
                self.ln(10)
                
            def footer(self):
                # Position at 1.5 cm from bottom
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.set_text_color(100, 100, 100)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
                
        # Create PDF object with custom branding
        pdf = PDF(company_name, brand_color, logo_size, include_timestamp)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Add executive summary
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(30, 58, 138)  # Dark blue color
        pdf.cell(0, 10, 'Executive Summary', 0, 1, 'L')
        
        # Add a fancy box around summary stats
        pdf.set_fill_color(239, 246, 255)  # Light blue background
        pdf.set_draw_color(199, 210, 254)  # Border color
        pdf.rect(10, pdf.get_y(), 190, 25, 'DF')
        
        # Add summary text
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(15, pdf.get_y() + 5)
        
        # Summary metrics in a cleaner format
        if 'Age_Numeric' in dataframe.columns:
            avg_age = dataframe['Age_Numeric'].mean()
            urgent_count = len(dataframe[dataframe['Priority'].str.contains('Urgent', case=False, na=False)])
            open_count = len(dataframe[dataframe['Status'].str.contains('Open|New|In Progress', case=False, na=False)])
            
            summary_text = (
                f"This report contains details on {len(dataframe)} security tickets. "
                f"The average ticket age is {avg_age:.1f} days with {urgent_count} urgent issues. "
                f"Currently, {open_count} tickets require attention."
            )
            
            # Add text with line breaks if needed
            pdf.multi_cell(180, 5, summary_text)
        else:
            pdf.multi_cell(180, 5, f"This report contains details on {len(dataframe)} security tickets.")
            
        pdf.ln(10)
        
        # Add priority distribution section with colored legend
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 10, 'Ticket Priority Distribution', 0, 1, 'L')
        
        # Count tickets by priority
        priority_counts = {
            'Urgent': len(dataframe[dataframe['Priority'].str.contains('Urgent', case=False, na=False)]),
            'High': len(dataframe[dataframe['Priority'].str.contains('High', case=False, na=False)]),
            'Medium': len(dataframe[dataframe['Priority'].str.contains('Medium', case=False, na=False)]),
            'Low': len(dataframe[dataframe['Priority'].str.contains('Low', case=False, na=False)])
        }
        
        # Create colored boxes for priorities
        pdf.set_font('Arial', 'B', 10)
        
        # Urgent - Red
        pdf.set_fill_color(239, 68, 68)
        pdf.set_text_color(255, 255, 255)
        pdf.rect(15, pdf.get_y() + 2, 8, 8, 'F')
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(25, pdf.get_y() + 2)
        pdf.cell(30, 8, f"Urgent: {priority_counts['Urgent']}", 0, 0)
        
        # High - Orange
        pdf.set_fill_color(245, 158, 11)
        pdf.rect(65, pdf.get_y(), 8, 8, 'F')
        pdf.set_xy(75, pdf.get_y())
        pdf.cell(30, 8, f"High: {priority_counts['High']}", 0, 0)
        
        # Medium - Yellow
        pdf.set_fill_color(251, 191, 36)
        pdf.rect(115, pdf.get_y(), 8, 8, 'F')
        pdf.set_xy(125, pdf.get_y())
        pdf.cell(30, 8, f"Medium: {priority_counts['Medium']}", 0, 0)
        
        # Low - Green
        pdf.set_fill_color(16, 185, 129)
        pdf.rect(165, pdf.get_y(), 8, 8, 'F')
        pdf.set_xy(175, pdf.get_y())
        pdf.cell(30, 8, f"Low: {priority_counts['Low']}", 0, 1)
        
        # Add a clean page break between sections
        pdf.add_page()
        
        # Add charts and visualizations from the dashboard
        
        # Create Ticket Status Distribution with matplotlib horizontal bar chart
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 10, 'Ticket Status Distribution', 0, 1, 'L')
        
        # Get status data from actual dataframe
        if 'Status' in dataframe.columns:
            # Calculate status counts and percentages
            status_counts = dataframe['Status'].value_counts()
            total_tickets = len(dataframe)
            
            # Get top 8 statuses
            top_statuses = status_counts.head(8)
            
            # Prepare data for plotting
            statuses = list(top_statuses.index)
            counts = list(top_statuses.values)
            percentages = [(count / total_tickets) * 100 for count in counts]
        
        # Colors for each status
        colors = [
            "#4c81d1", "#f5a623", "#9b9b9b", "#f8e71c", 
            "#bd10e0", "#7ed321", "#50e3c2", "#d0021b"
        ]
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot horizontal bars with only needed colors
        colors_needed = colors[:len(statuses)]
        bars = ax.barh(statuses, counts, color=colors_needed)
        
        # Adding text labels, right aligned
        for i, (bar, pct) in enumerate(zip(bars, percentages)):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height() / 2,
                    f"{counts[i]} ({pct:.1f}%)", va='center', ha='left', fontsize=10)
        
        # Aesthetics
        ax.set_xlabel('Number of Tickets')
        ax.set_title('Ticket Status Distribution', fontsize=14, fontweight='bold')
        ax.invert_yaxis()  # Highest value on top
        ax.set_xlim(0, max(counts) + 20)  # Add margin for label visibility
        plt.tight_layout()
        
        # Save the plot to a temporary file
        temp_img_path = '/tmp/status_chart.png'
        plt.savefig(temp_img_path, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        # Add the plot to the PDF
        pdf.image(temp_img_path, x=25, y=None, w=160)
        
        pdf.ln(10)
        
        # Top 10 Tickets by Company section - now on the same page, no add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 10, 'Top 10 Tickets by Company', 0, 1, 'L')
        
        if 'Company' in dataframe.columns:
            # Get top 10 companies by ticket count
            company_counts = dataframe['Company'].value_counts().head(10)
            
            # Create table header with colored background
            pdf.set_fill_color(239, 246, 255)  # Light blue background
            pdf.set_text_color(30, 58, 138)    # Dark blue text
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(135, 8, 'Company Name', 1, 0, 'C', 1)
            pdf.cell(45, 8, 'Ticket Count', 1, 1, 'C', 1)
            
            # Add table data
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(0, 0, 0)
            
            # Alternate row colors for better readability
            row_color = False
            
            # Total for percentage calculation
            total_tickets = len(dataframe)
            
            for company, count in company_counts.items():
                # Format company name consistently
                company_name = company
                if len(company_name) > 35:
                    company_name = company_name[:32] + '...'
                
                # Calculate percentage
                percentage = (count / total_tickets) * 100
                
                # Set fill color for alternating rows
                if row_color:
                    pdf.set_fill_color(249, 250, 251)  # Light grey
                else:
                    pdf.set_fill_color(255, 255, 255)  # White
                
                # Add data cells
                pdf.cell(135, 7, company_name, 1, 0, 'L', row_color)
                pdf.cell(45, 7, str(count), 1, 1, 'C', row_color)
                
                row_color = not row_color  # Alternate row color
        
        pdf.ln(15)
        
        # Move to page 2
        pdf.add_page()
        
        # Add Top of Done Yets table including Resources column
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 10, 'Top Done Yets', 0, 1, 'L')
        
        # Add descriptive text for Done Yets table
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 5, 'The following table shows tickets with "Done yet?" status, requiring final verification:')
        pdf.ln(5)
        
        # Get tickets with "Done yet?" status
        if 'Status' in dataframe.columns:
            done_yet_tickets = dataframe[dataframe['Status'].str.contains('Done yet', case=False, na=False)].head(5)
            
            if not done_yet_tickets.empty:
                # Create table header with colored background
                pdf.set_fill_color(239, 246, 255)  # Light blue background
                pdf.set_text_color(30, 58, 138)    # Dark blue text
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(20, 7, 'Ticket #', 1, 0, 'C', 1)
                pdf.cell(15, 7, 'Age', 1, 0, 'C', 1)
                pdf.cell(35, 7, 'Company', 1, 0, 'C', 1)
                pdf.cell(35, 7, 'Resource', 1, 0, 'C', 1)
                pdf.cell(85, 7, 'Summary', 1, 1, 'C', 1)
                
                # Add table data
                pdf.set_font('Arial', '', 8)
                pdf.set_text_color(0, 0, 0)
                
                # Alternate row colors for better readability
                row_color = False
                
                for _, row in done_yet_tickets.iterrows():
                    # Get values with fallback for missing columns
                    ticket_num = str(row.get('Ticket #', 'N/A'))
                    priority = str(row.get('Priority', 'N/A'))
                    age = str(row.get('Age', 'N/A')) if 'Age' in row else 'N/A'
                    company = str(row.get('Company', 'N/A'))
                    resource = str(row.get('Resources', 'N/A'))
                    summary = str(row.get('Summary Description', 'N/A'))
                    
                    # Truncate long fields
                    if len(summary) > 45:
                        summary = summary[:42] + '...'
                    if len(company) > 12:
                        company = company[:9] + '...'
                    if len(resource) > 12:
                        resource = resource[:9] + '...'
                    
                    # Set fill color for alternating rows
                    if row_color:
                        pdf.set_fill_color(249, 250, 251)  # Light grey
                    else:
                        pdf.set_fill_color(255, 255, 255)  # White
                    
                    # Add data cells
                    pdf.cell(20, 7, ticket_num[:9], 1, 0, 'L', row_color)
                    pdf.cell(15, 7, age[:9], 1, 0, 'L', row_color)
                    pdf.cell(35, 7, company, 1, 0, 'L', row_color)
                    pdf.cell(35, 7, resource, 1, 0, 'L', row_color)
                    pdf.cell(85, 7, summary, 1, 1, 'L', row_color)
                    
                    row_color = not row_color  # Alternate row color
            else:
                pdf.set_font('Arial', 'I', 10)
                pdf.cell(0, 10, 'No tickets with "Done yet?" status found in the current dataset.', 0, 1, 'L')
            
            pdf.ln(20)
        
        # Move to page 3 for Top 10 Oldest Tickets
        pdf.add_page()
        
        # 4. Top 10 oldest tickets section - Now with Resources column
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(30, 58, 138)
        pdf.cell(0, 10, 'Top 10 Oldest Tickets', 0, 1, 'L')
        
        if 'Age_Numeric' in dataframe.columns:
            oldest = dataframe.sort_values('Age_Numeric', ascending=False).head(10)
            
            # Create table header with colored background
            pdf.set_fill_color(239, 246, 255)  # Light blue background
            pdf.set_text_color(30, 58, 138)    # Dark blue text
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(20, 7, 'Ticket #', 1, 0, 'C', 1)
            pdf.cell(15, 7, 'Age', 1, 0, 'C', 1)
            pdf.cell(35, 7, 'Company', 1, 0, 'C', 1)
            pdf.cell(35, 7, 'Resource', 1, 0, 'C', 1)
            pdf.cell(85, 7, 'Summary', 1, 1, 'C', 1)
            
            # Add table data
            pdf.set_font('Arial', '', 8)
            pdf.set_text_color(0, 0, 0)
            
            # Alternate row colors for better readability
            row_color = False
            
            for _, row in oldest.iterrows():
                # Get values with fallback for missing columns
                ticket_num = str(row.get('Ticket #', 'N/A'))
                priority = str(row.get('Priority', 'N/A'))
                age = str(row.get('Age', 'N/A'))
                status = str(row.get('Status', 'N/A'))
                company = str(row.get('Company', 'N/A'))
                resource = str(row.get('Resources', 'N/A'))
                summary = str(row.get('Summary Description', 'N/A'))
                
                # Truncate long fields
                if len(summary) > 40:
                    summary = summary[:37] + '...'
                if len(company) > 12:
                    company = company[:9] + '...'
                if len(resource) > 12:
                    resource = resource[:9] + '...'
                
                # Set fill color for alternating rows
                if row_color:
                    pdf.set_fill_color(249, 250, 251)  # Light grey
                else:
                    pdf.set_fill_color(255, 255, 255)  # White
                
                # Add data cells
                pdf.cell(20, 7, ticket_num[:9], 1, 0, 'L', row_color)
                pdf.cell(15, 7, age[:9], 1, 0, 'L', row_color)
                pdf.cell(35, 7, company, 1, 0, 'L', row_color)
                pdf.cell(35, 7, resource, 1, 0, 'L', row_color)
                pdf.cell(85, 7, summary, 1, 1, 'L', row_color)
                
                row_color = not row_color  # Alternate row color
        
        # No contact information footer as requested
        
        # Fix for byte array encoding issue
        try:
            # First attempt with latin1 encoding
            return pdf.output(dest='S').encode('latin1')
        except (UnicodeEncodeError, AttributeError):
            # Fallback if the first method fails
            byte_string = pdf.output(dest='S')
            if isinstance(byte_string, str):
                return byte_string.encode('latin1')
            return byte_string
    
    # Simple PDF export section - no heading
    # Add some spacing
    st.write("")
    
    # Fixed default values
    company_name = "COMPANY"
    rgb_color = (41, 128, 185)  # Default blue
    logo_size = 20  # Fixed logo size as requested
    include_timestamp = True
    
    # Center download button with wider margins
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col2:
        try:
            pdf_data = create_pdf(filtered_df, company_name, rgb_color, logo_size, include_timestamp)
            
            # Add custom styling to center the button
            st.markdown(
                """
                <style>
                div.stDownloadButton > button {
                    width: 100%;
                    text-align: center;
                    font-weight: bold;
                }
                </style>
                """, 
                unsafe_allow_html=True
            )
            
            st.download_button(
                label="🔽 Download Executive Report (PDF)",
                data=pdf_data,
                file_name=f"Daily_Insights_{datetime.now().strftime('%d_%B_%Y')}.pdf",
                mime="application/pdf",
                help="Download a comprehensive PDF report with executive summary and detailed ticket metrics",
                key="pdf_download"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            
            # Add more detailed error info for debugging
            import traceback
            st.error(f"Error details: {traceback.format_exc()}")
            st.info("There was an issue with the PDF generation. Please try again.")
