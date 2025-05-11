import streamlit as st
import pandas as pd
from sqlalchemy import text
from utils.database_fixed import get_engine

# Page configuration
st.set_page_config(
    page_title="Project Settings | Open Source Dashboard",
    page_icon="⚙️",
    layout="wide"
)

# Title and description
st.title("⚙️ Project Settings")
st.markdown("Configure your open source project settings to customize the dashboard.")

# Function to get current settings
def get_project_settings():
    engine = get_engine()
    if not engine:
        st.error("Database connection failed. Cannot load settings.")
        return {
            "project_name": "Open Source Project",
            "project_description": "An amazing open source project",
            "project_repo": "https://github.com/organization/repo",
            "target_contributors": "50",
            "current_contributors": "10"
        }
    
    try:
        # Query all settings
        query = "SELECT key, value FROM project_settings;"
        df = pd.read_sql(query, engine)
        
        # Convert to dictionary
        settings = {}
        for _, row in df.iterrows():
            settings[row['key']] = row['value']
        
        # Set defaults for any missing settings
        default_settings = {
            "project_name": "Open Source Project",
            "project_description": "An amazing open source project",
            "project_repo": "https://github.com/organization/repo",
            "target_contributors": "50",
            "current_contributors": "10"
        }
        
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
                
        return settings
    except Exception as e:
        st.error(f"Error loading settings: {e}")
        return {
            "project_name": "Open Source Project",
            "project_description": "An amazing open source project",
            "project_repo": "https://github.com/organization/repo",
            "target_contributors": "50",
            "current_contributors": "10"
        }

# Function to update settings
def update_project_settings(settings):
    engine = get_engine()
    if not engine:
        st.error("Database connection failed. Cannot update settings.")
        return False
    
    try:
        with engine.connect() as conn:
            for key, value in settings.items():
                # Check if setting exists
                result = conn.execute(text(f"SELECT COUNT(*) FROM project_settings WHERE key = '{key}'"))
                if result.scalar() > 0:
                    # Update existing setting
                    conn.execute(text(f"UPDATE project_settings SET value = '{value}', updated_at = '{datetime.now().date()}' WHERE key = '{key}'"))
                else:
                    # Insert new setting
                    conn.execute(text(f"INSERT INTO project_settings (key, value) VALUES ('{key}', '{value}')"))
            
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating settings: {e}")
        return False

# Get current settings
current_settings = get_project_settings()

# Create form for editing settings
with st.form("project_settings_form"):
    st.subheader("Basic Project Information")
    
    project_name = st.text_input(
        "Project Name",
        value=current_settings.get("project_name", "Open Source Project")
    )
    
    project_description = st.text_area(
        "Project Description",
        value=current_settings.get("project_description", "An amazing open source project"),
        height=100
    )
    
    project_repo = st.text_input(
        "Project Repository URL",
        value=current_settings.get("project_repo", "https://github.com/organization/repo")
    )
    
    st.subheader("Growth Targets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_contributors = st.number_input(
            "Current Contributors",
            min_value=0,
            value=int(current_settings.get("current_contributors", 10))
        )
    
    with col2:
        target_contributors = st.number_input(
            "Target Contributors",
            min_value=1,
            value=int(current_settings.get("target_contributors", 50))
        )
    
    # Submit button
    submitted = st.form_submit_button("Save Settings")
    
    if submitted:
        # Update settings
        new_settings = {
            "project_name": project_name,
            "project_description": project_description,
            "project_repo": project_repo,
            "current_contributors": str(current_contributors),
            "target_contributors": str(target_contributors)
        }
        
        if update_project_settings(new_settings):
            st.success("Settings updated successfully!")
        else:
            st.error("Failed to update settings.")

# Import datetime for the timestamp
from datetime import datetime

# Display tips about how these settings are used
st.markdown("---")
st.subheader("How Settings Are Used")
st.markdown("""
- **Project Name**: Displayed in the header and title of all dashboard pages
- **Project Description**: Shown in the Community Resources page and used in documentation
- **Repository URL**: Used for links to GitHub and documentation
- **Current & Target Contributors**: Used for progress charts and growth metrics
""")

# footer
st.markdown("---")
st.caption("Open Source Community Dashboard - Helping grow your community")