import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Database Admin | Gaia Open Source",
    page_icon="🌱",
    layout="wide"
)

# Import modules after page config
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database functions after page config
from utils.database_fixed import get_engine, add_contributor, add_contribution, update_project_metrics

# Header
st.title("⚙️ Database Administration")
st.markdown("""
This page allows administrators to manage the database for the Gaia Open Source Community Dashboard.
You can add contributors, record contributions, and view/update project metrics.
""")

# Check database connection
db_engine = get_engine()
if db_engine:
    st.success("Connected to database successfully")
else:
    st.error("Database connection not configured or failed")
    st.info("Please set the DATABASE_URL environment variable with a valid PostgreSQL connection string")
    st.stop()

# Main content - split into tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Add Contributors", 
    "Record Contributions", 
    "Update Metrics",
    "View Data"
])

with tab1:
    st.header("Add New Contributor")
    
    with st.form("add_contributor_form"):
        username = st.text_input("GitHub Username", help="The contributor's GitHub username")
        display_name = st.text_input("Display Name (Optional)", help="The contributor's full name for display")
        email = st.text_input("Email (Optional)", help="Contact email for the contributor")
        
        contribution_type = st.selectbox(
            "Primary Contribution Type",
            ["code", "documentation", "design", "testing", "community"],
            help="The main type of contributions this person makes"
        )
        
        first_contribution_date = st.date_input(
            "First Contribution Date",
            value=datetime.now(),
            help="When this person first contributed to the project"
        )
        
        submit_contributor = st.form_submit_button("Add Contributor")
    
    if submit_contributor:
        if username:
            success = add_contributor(
                username=username,
                first_contribution_date=first_contribution_date,
                contribution_type=contribution_type,
                email=email if email else None,
                display_name=display_name if display_name else None
            )
            
            if success:
                st.success(f"Added contributor: {username}")
            else:
                st.error("Failed to add contributor. Check the logs for details.")
        else:
            st.warning("GitHub Username is required")

with tab2:
    st.header("Record Contribution")
    
    with st.form("add_contribution_form"):
        contributor_username = st.text_input("Contributor Username", help="GitHub username of the contributor")
        
        contribution_type = st.selectbox(
            "Contribution Type",
            ["pull_request", "issue", "comment", "documentation", "design", "code_review"],
            help="The type of contribution"
        )
        
        contribution_date = st.date_input(
            "Contribution Date",
            value=datetime.now(),
            help="When this contribution was made"
        )
        
        title = st.text_input("Title/Description", help="Brief title or description of the contribution")
        description = st.text_area("Detailed Description (Optional)", help="More details about the contribution")
        url = st.text_input("URL (Optional)", help="Link to the contribution (e.g., PR or issue URL)")
        
        status = st.selectbox(
            "Status",
            ["open", "closed", "merged", "completed"],
            help="Current status of this contribution"
        )
        
        submit_contribution = st.form_submit_button("Record Contribution")
    
    if submit_contribution:
        if contributor_username and title:
            success = add_contribution(
                contributor_username=contributor_username,
                date=contribution_date,
                contribution_type=contribution_type,
                title=title,
                description=description if description else None,
                url=url if url else None,
                status=status
            )
            
            if success:
                st.success(f"Recorded contribution from: {contributor_username}")
            else:
                st.error("Failed to record contribution. Check the logs for details.")
        else:
            st.warning("Contributor Username and Title are required")

with tab3:
    st.header("Update Project Metrics")
    
    with st.form("update_metrics_form"):
        metrics_date = st.date_input(
            "Date",
            value=datetime.now(),
            help="Date for these metrics"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            total_contributors = st.number_input("Total Contributors", value=0, min_value=0)
            active_contributors = st.number_input("Active Contributors (Last 30 days)", value=0, min_value=0)
            open_issues = st.number_input("Open Issues", value=0, min_value=0)
            closed_issues = st.number_input("Closed Issues", value=0, min_value=0)
        
        with col2:
            open_prs = st.number_input("Open Pull Requests", value=0, min_value=0)
            merged_prs = st.number_input("Merged Pull Requests", value=0, min_value=0)
            stars = st.number_input("GitHub Stars", value=0, min_value=0)
            forks = st.number_input("GitHub Forks", value=0, min_value=0)
        
        submit_metrics = st.form_submit_button("Update Metrics")
    
    if submit_metrics:
        metrics_data = {
            'total_contributors': total_contributors,
            'active_contributors': active_contributors,
            'open_issues': open_issues,
            'closed_issues': closed_issues,
            'open_prs': open_prs,
            'merged_prs': merged_prs,
            'stars': stars,
            'forks': forks
        }
        
        success = update_project_metrics(metrics_date, metrics_data)
        
        if success:
            st.success(f"Updated project metrics for: {metrics_date}")
        else:
            st.error("Failed to update metrics. Check the logs for details.")

with tab4:
    st.header("View Database Data")
    
    table_selection = st.selectbox(
        "Select Table",
        ["contributors", "contributions", "project_metrics"]
    )
    
    if table_selection:
        try:
            query = f"SELECT * FROM {table_selection} ORDER BY id DESC LIMIT 100;"
            df = pd.read_sql(query, db_engine)
            
            st.subheader(f"{table_selection.capitalize()} Data")
            st.dataframe(df)
            
            if not df.empty:
                st.download_button(
                    label=f"Download {table_selection} data as CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"{table_selection}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime='text/csv',
                )
            else:
                st.info(f"No data found in {table_selection} table")
                
        except Exception as e:
            st.error(f"Error retrieving data: {e}")

# footer
st.markdown("---")
st.caption("Gaia Open Source Community Dashboard - Helping grow our community from 10 to 50 active contributors")