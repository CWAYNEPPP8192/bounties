import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Database Connection Test | Open Source Dashboard",
    page_icon="🌱",
    layout="wide"
)

# Import modules after page config
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import urllib.parse
from utils.database_fixed import get_engine

# Load environment variables
load_dotenv()

# Get project info from database
engine = get_engine()
project_name = "Open Source Project"
current_contributors = 10
target_contributors = 50

if engine:
    try:
        # Get project name
        query = "SELECT value FROM project_settings WHERE key = 'project_name';"
        df = pd.read_sql(query, engine)
        if not df.empty:
            project_name = df.iloc[0]['value']
            
        # Get current contributors
        query = "SELECT value FROM project_settings WHERE key = 'current_contributors';"
        df = pd.read_sql(query, engine)
        if not df.empty:
            current_contributors = int(df.iloc[0]['value'])
            
        # Get target contributors
        query = "SELECT value FROM project_settings WHERE key = 'target_contributors';"
        df = pd.read_sql(query, engine)
        if not df.empty:
            target_contributors = int(df.iloc[0]['value'])
    except Exception as e:
        st.error(f"Error loading project settings: {e}")

# Header
st.title("🔌 Database Connection Test")
st.markdown(f"""
This page allows you to test the database connection for the {project_name} Community Dashboard.
""")

# Get SQLite path and PostgreSQL URL
import os.path
SQLITE_DB_PATH = os.path.join(os.getcwd(), 'gaia_community.db')
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"
DATABASE_URL = os.environ.get('DATABASE_URL')

# Display current connection details
st.subheader("Current Database Configuration")

st.success(f"Using SQLite database at: {SQLITE_DB_PATH}")
st.markdown("""
SQLite is configured for local development and doesn't require any external connection. 
All data will be stored in a local file.
""")

if DATABASE_URL:
    st.info("PostgreSQL configuration is also available but not currently used.")
    # Redact password for display
    try:
        parts = DATABASE_URL.split('@')
        auth_part = parts[0].split(':')
        redacted_url = f"{auth_part[0]}:****@{parts[1]}"
        st.code(redacted_url)
    except Exception:
        st.code("Unable to parse PostgreSQL URL format")
else:
    st.info("No PostgreSQL configuration found in environment variables. Using SQLite only.")

# Function to test database connection
def test_database_connection(url):
    """Test if the database connection is working properly."""
    if not url:
        return {
            "success": False,
            "message": "No database connection string provided."
        }
    
    # Remove quotes if present
    if url.startswith('"') and url.endswith('"'):
        url = url[1:-1]
    
    # If url starts with postgres://, replace with postgresql:// (SQLAlchemy requirement)
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
        
    try:
        # Create engine and try a simple query
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.fetchone():
                return {
                    "success": True,
                    "message": "Database connection successful!",
                    "engine": engine
                }
    except Exception as e:
        return {
            "success": False,
            "message": f"Database connection error: {str(e)}"
        }

# Add ability to test a custom connection string
st.subheader("Test Connection")

# Option to use current or custom connection string
use_custom = st.checkbox("Use custom connection string")

if use_custom:
    custom_url = st.text_input("Custom Database URL", type="password")
    connection_string = custom_url
else:
    connection_string = DATABASE_URL

# Buttons to test connection
if st.button("Test Database Connection"):
    if not connection_string:
        st.error("No connection string provided.")
    else:
        with st.spinner("Testing connection..."):
            result = test_database_connection(connection_string)
            
            if result["success"]:
                st.success(result["message"])
                
                # If connection works, offer to create tables
                if st.button("Initialize Database Tables"):
                    try:
                        engine = result["engine"]
                        
                        # Define SQL for creating tables
                        create_tables_sql = """
                        CREATE TABLE IF NOT EXISTS contributors (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(100) UNIQUE NOT NULL,
                            first_contribution_date DATE NOT NULL,
                            contribution_count INTEGER DEFAULT 0,
                            is_active BOOLEAN DEFAULT TRUE,
                            contribution_type VARCHAR(50),
                            email VARCHAR(100),
                            display_name VARCHAR(100)
                        );
                        
                        CREATE TABLE IF NOT EXISTS contributions (
                            id SERIAL PRIMARY KEY,
                            contributor_id INTEGER REFERENCES contributors(id),
                            date DATE NOT NULL,
                            type VARCHAR(50) NOT NULL, 
                            title VARCHAR(255),
                            description TEXT,
                            url VARCHAR(255),
                            status VARCHAR(50)
                        );
                        
                        CREATE TABLE IF NOT EXISTS project_metrics (
                            id SERIAL PRIMARY KEY,
                            date DATE UNIQUE NOT NULL,
                            total_contributors INTEGER,
                            active_contributors INTEGER,
                            open_issues INTEGER,
                            closed_issues INTEGER,
                            open_prs INTEGER,
                            merged_prs INTEGER,
                            stars INTEGER,
                            forks INTEGER
                        );
                        """
                        
                        # Execute the SQL
                        with engine.connect() as conn:
                            conn.execute(text(create_tables_sql))
                            conn.commit()
                            
                        st.success("Database tables initialized successfully!")
                    except Exception as e:
                        st.error(f"Error initializing tables: {str(e)}")
            else:
                st.error(result["message"])

# Add troubleshooting tips
st.subheader("Troubleshooting Tips")
st.markdown("""
If you're having trouble connecting to the database, check the following:

1. **Connection String Format**: Make sure your connection string is in the correct format:
   ```
   postgresql://username:password@host:port/database
   ```

2. **Special Characters**: If your password contains special characters, they should be URL-encoded.
   For example, replace:
   - `@` with `%40`
   - `#` with `%23`
   - `$` with `%24`
   - `&` with `%26`

3. **Port**: Verify that the correct port number is specified in the connection string.

4. **Network**: Ensure that the database server is accessible from this application.

5. **Credentials**: Double-check your username and password for accuracy.

6. **Database Existence**: Confirm that the specified database exists on the server.
""")

# footer
st.markdown("---")
st.caption(f"{project_name} Community Dashboard - Helping grow our community from {current_contributors} to {target_contributors} active contributors")