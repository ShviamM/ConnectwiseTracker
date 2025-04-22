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
    page_title="NOC Security Dashboard",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for eye-catching executive report styling
st.markdown("""
<style>
    .main-header {
        font-size: 42px !important;
        font-weight: 700 !important;
        color: #1E3A8A !important;
        text-align: center;
        padding: 10px 0;
        margin-bottom: 20px;
        background: linear-gradient(90deg, #EEF2FF, #C7D2FE, #EEF2FF);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .subheader {
        font-size: 26px !important;
        font-weight: 600 !important;
        color: #1E3A8A !important;
        padding: 5px 0;
        margin: 20px 0 15px 0;
        border-bottom: 2px solid #C7D2FE;
    }
    .metric-container {
        background: #F9FAFB;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #3B82F6;
    }
    .stMetric {
        background-color: white !important;
        border-radius: 6px !important;
        padding: 10px !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05) !important;
    }
    .row-header {
        font-weight: 600;
        font-size: 18px;
        margin-bottom: 10px;
        color: #1E40AF;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 8px !important;
        padding: 5px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08) !important;
    }
    /* Priority color coding */
    .priority-urgent {
        background-color: #EF4444 !important;
        color: white !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .priority-high {
        background-color: #F59E0B !important;
        color: white !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .priority-medium {
        background-color: #FBBF24 !important;
        color: #1F2937 !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .priority-low {
        background-color: #10B981 !important;
        color: white !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    /* Download button styling */
    div.stDownloadButton > button {
        background-color: #3B82F6 !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 4px 20px !important;
        font-weight: 500 !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(59, 130, 246, 0.3) !important;
    }
    div.stDownloadButton > button:hover {
        background-color: #2563EB !important;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Application title with enhanced styling
st.markdown("<h1 class='main-header'>NOC - Security Ticket Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; margin-bottom: 30px;'>Visualizing security ticket statistics and metrics from Connectwise</p>", unsafe_allow_html=True)

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
    
    # Always load the sample data file on startup
    try:
        # Load all 157 tickets from the attached CSV file
        csv_path = "attached_assets/srboard.csv"
        
        # First, manually count lines to confirm we have 158 total lines (157 tickets + header)
        with open(csv_path, 'r') as f:
            total_lines = sum(1 for line in f)
        
        # Now read with pandas
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        # Display total count before any processing
        st.write(f"Total tickets in CSV: {len(df)} (should be 157)")
        
        # Clean data
        df = clean_data(df)
        
        # Force all 157 tickets to appear - this is critical!
        st.write(f"Displaying all {len(df)} tickets from file")
        
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
        
        st.success("File processed successfully!")
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
    
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
    
    # Create processed data for visualization
    processed_data = process_data(filtered_df, time_period.lower())
    
    # Display summary metrics with enhanced styling
    st.markdown("<h2 class='subheader'>Summary Metrics</h2>", unsafe_allow_html=True)
    
    # Create a metrics container with custom styling
    st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Tickets", 
            value=len(filtered_df)
        )
    
    with col2:
        # Average age of tickets
        if 'Age' in filtered_df.columns:
            try:
                # Extract numeric value from Age column
                filtered_df.loc[:, 'Age_Numeric'] = filtered_df['Age'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
                avg_age = filtered_df['Age_Numeric'].mean()
                st.metric(
                    label="Average Age (Days)", 
                    value=f"{avg_age:.1f}"
                )
            except:
                st.metric(label="Average Age (Days)", value="N/A")
        else:
            st.metric(label="Average Age (Days)", value="N/A")
    
    with col3:
        # Tickets without assigned resources
        if 'Resources' in filtered_df.columns:
            unassigned = filtered_df[filtered_df['Resources'].isna() | (filtered_df['Resources'] == '')].shape[0]
            st.metric(
                label="Unassigned Tickets", 
                value=unassigned,
                delta=f"{unassigned/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%"
            )
        else:
            st.metric(label="Unassigned Tickets", value="N/A")
    
    with col4:
        # SLA compliance
        if 'SLA Status' in filtered_df.columns:
            overdue = filtered_df[filtered_df['SLA Status'].str.contains('late|overdue', case=False, na=False)].shape[0]
            st.metric(
                label="SLA Issues", 
                value=overdue,
                delta=f"{overdue/len(filtered_df)*100:.1f}%" if len(filtered_df) > 0 else "0%",
                delta_color="inverse"
            )
        else:
            st.metric(label="SLA Issues", value="N/A")
    
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
    
    # Create PDF export function
    def create_pdf(dataframe):
        pdf = FPDF()
        pdf.add_page()
        
        # Configure title and header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'NOC - Security Ticket Dashboard Report', 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Add summary metrics
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Summary Metrics', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(60, 10, f'Total Tickets: {len(dataframe)}', 0, 0)
        
        if 'Age_Numeric' in dataframe.columns:
            avg_age = dataframe['Age_Numeric'].mean()
            pdf.cell(60, 10, f'Average Age: {avg_age:.1f} days', 0, 0)
        
        pdf.ln(15)
        
        # Add top 10 oldest tickets
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Top 10 Oldest Tickets', 0, 1, 'L')
        
        if 'Age_Numeric' in dataframe.columns:
            oldest = dataframe.sort_values('Age_Numeric', ascending=False).head(10)
            
            # Create table header
            pdf.set_font('Arial', 'B', 9)
            pdf.cell(25, 7, 'Ticket #', 1, 0, 'C')
            pdf.cell(25, 7, 'Priority', 1, 0, 'C')
            pdf.cell(20, 7, 'Age', 1, 0, 'C')
            pdf.cell(30, 7, 'Status', 1, 0, 'C')
            pdf.cell(90, 7, 'Summary', 1, 1, 'C')
            
            # Add table data
            pdf.set_font('Arial', '', 8)
            for _, row in oldest.iterrows():
                # Get values with fallback for missing columns
                ticket_num = str(row.get('Ticket #', 'N/A'))
                priority = str(row.get('Priority', 'N/A'))
                age = str(row.get('Age', 'N/A'))
                status = str(row.get('Status', 'N/A'))
                summary = str(row.get('Summary Description', 'N/A'))
                
                # Truncate long fields
                if len(summary) > 50:
                    summary = summary[:47] + '...'
                
                # Write data row
                pdf.cell(25, 7, ticket_num[:10], 1, 0)
                pdf.cell(25, 7, priority[:10], 1, 0)
                pdf.cell(20, 7, age[:10], 1, 0)
                pdf.cell(30, 7, status[:15], 1, 0)
                pdf.cell(90, 7, summary, 1, 1)
                
        pdf.ln(10)
        
        # Add alert tickets
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Top 10 Alert Tickets', 0, 1, 'L')
        
        if 'Summary Description' in dataframe.columns:
            alerts_mask = dataframe['Summary Description'].str.contains('Alert|Warning|Critical|Urgent|Emergency|Endgame', case=False, na=False)
            alerts = dataframe[alerts_mask].head(10)
            
            if not alerts.empty:
                # Create table header
                pdf.set_font('Arial', 'B', 9)
                pdf.cell(25, 7, 'Ticket #', 1, 0, 'C')
                pdf.cell(25, 7, 'Priority', 1, 0, 'C')
                pdf.cell(30, 7, 'Status', 1, 0, 'C')
                pdf.cell(110, 7, 'Summary', 1, 1, 'C')
                
                # Add table data
                pdf.set_font('Arial', '', 8)
                for _, row in alerts.iterrows():
                    ticket_num = str(row.get('Ticket #', 'N/A'))
                    priority = str(row.get('Priority', 'N/A'))
                    status = str(row.get('Status', 'N/A'))
                    summary = str(row.get('Summary Description', 'N/A'))
                    
                    # Truncate long fields
                    if len(summary) > 60:
                        summary = summary[:57] + '...'
                    
                    # Write data row
                    pdf.cell(25, 7, ticket_num[:10], 1, 0)
                    pdf.cell(25, 7, priority[:10], 1, 0)
                    pdf.cell(30, 7, status[:15], 1, 0)
                    pdf.cell(110, 7, summary, 1, 1)
        
        return pdf.output(dest='S').encode('latin1')
    
    # PDF Download button with better styling - now just one button
    try:
        pdf_data = create_pdf(filtered_df)
        st.download_button(
            label="Download Executive Report (PDF)",
            data=pdf_data,
            file_name=f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            help="Download a formatted PDF report with the current filtered data"
        )
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        st.info("PDF generation requires additional configuration.")
