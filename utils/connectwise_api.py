import requests
import base64
import json
import pandas as pd
from datetime import datetime

def get_connectwise_tickets(site_url, company_id, public_key, private_key, client_id=None, conditions=None, page_size=1000):
    """
    Fetch tickets from ConnectWise API
    
    Args:
        site_url: The ConnectWise site URL
        company_id: Company ID for the ConnectWise API
        public_key: Public key for the ConnectWise API
        private_key: Private key for the ConnectWise API
        client_id: Client ID for the ConnectWise API
        conditions: Additional query conditions (optional)
        page_size: Number of records to fetch per page
        
    Returns:
        DataFrame containing ticket data
    """
    # Create the authentication string
    auth_string = f"{company_id}+{public_key}:{private_key}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    # Setup headers
    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/json"
    }
    
    # Add clientId if provided
    if client_id:
        headers["clientId"] = client_id
    else:
        headers["clientId"] = company_id
    
    # Setup API URL
    api_url = f"{site_url}/v4_6_release/apis/3.0/service/tickets"
    
    # Define parameters
    params = {"pageSize": page_size}
    
    # Add conditions if provided
    if conditions:
        params["conditions"] = conditions
    
    try:
        # Make the API request
        response = requests.get(api_url, headers=headers, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            tickets = response.json()
            return process_tickets_data(tickets)
        else:
            print(f"Error fetching tickets: {response.status_code} - {response.text}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return pd.DataFrame()

def process_tickets_data(tickets_raw):
    """
    Process raw ticket data from ConnectWise API into a DataFrame format
    that matches our dashboard's expected format
    
    Args:
        tickets_raw: Raw JSON data from ConnectWise API
        
    Returns:
        Processed DataFrame
    """
    # Create empty DataFrame if no tickets
    if not tickets_raw:
        return pd.DataFrame()
    
    # Create list to store processed ticket data
    processed_tickets = []
    
    for ticket in tickets_raw:
        # Extract and map ticket fields to match our dashboard's expected columns
        processed_ticket = {
            'Ticket #': ticket.get('id', ''),
            'Summary Description': ticket.get('summary', ''),
            'Status': ticket.get('status', {}).get('name', '') if ticket.get('status') else '',
            'Priority': map_priority_level(ticket.get('priority', {}).get('name', '') if ticket.get('priority') else ''),
            'Company': ticket.get('company', {}).get('name', '') if ticket.get('company') else '',
            'Resources': ticket.get('resources', {}).get('name', '') if ticket.get('resources') else '',
            'Team': ticket.get('team', {}).get('name', '') if ticket.get('team') else '',
            'Subtype': ticket.get('subType', {}).get('name', '') if ticket.get('subType') else '',
            'Last Update': format_datetime(ticket.get('lastUpdated', '')),
            'SLA Status': get_sla_status(ticket)
        }
        
        # Calculate age in days
        if ticket.get('dateEntered'):
            entered_date = datetime.fromisoformat(ticket.get('dateEntered').replace('Z', '+00:00'))
            age_days = (datetime.now() - entered_date).days
            processed_ticket['Age'] = f"{age_days} days"
            processed_ticket['Age_Numeric'] = age_days
        else:
            processed_ticket['Age'] = 'N/A'
            processed_ticket['Age_Numeric'] = 0
        
        processed_tickets.append(processed_ticket)
    
    # Convert to DataFrame
    return pd.DataFrame(processed_tickets)

def map_priority_level(priority_name):
    """Map ConnectWise priority names to our dashboard's priority levels"""
    # Modify this mapping based on ConnectWise priority names
    priority_map = {
        'Critical': 'Urgent',
        'Emergency': 'Urgent',
        'Priority 1': 'Urgent',
        'Priority 2': 'High',
        'Priority 3': 'Medium',
        'Priority 4': 'Low',
        'Priority 5': 'Low'
    }
    
    # Default to original name if not in mapping
    return priority_map.get(priority_name, priority_name)

def format_datetime(datetime_str):
    """Format API datetime string to match dashboard format"""
    if not datetime_str:
        return ''
    
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return datetime_str

def get_sla_status(ticket):
    """Determine SLA status from ticket information"""
    # This is a placeholder - adjust based on how SLA status is determined in ConnectWise
    if ticket.get('sla'):
        if ticket.get('sla').get('pastDue'):
            return 'Overdue'
        elif ticket.get('sla').get('responded'):
            return 'Responded'
    
    # Default status if not determined
    return 'Within SLA'