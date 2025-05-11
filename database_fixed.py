import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, MetaData, Table, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

# Set up SQLite database for local development
import os.path
SQLITE_DB_PATH = os.path.join(os.getcwd(), 'gaia_community.db')
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Also try to get PostgreSQL URL from environment variables as fallback
DATABASE_URL = os.environ.get('DATABASE_URL')
# Remove quotes if present
if DATABASE_URL and (DATABASE_URL.startswith('"') and DATABASE_URL.endswith('"')):
    DATABASE_URL = DATABASE_URL[1:-1]
# If url starts with postgres://, replace with postgresql:// (SQLAlchemy requirement)
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Print statement for debugging (will show in server logs)
print(f"Using SQLite database at: {SQLITE_DB_PATH}")
if DATABASE_URL:
    try:
        print(f"PostgreSQL URL also configured (redacted): {DATABASE_URL.split('@')[0]}@***")
    except Exception as e:
        print(f"Error processing PostgreSQL URL: {e}")

# Create database engine
@st.cache_resource
def get_engine():
    """Get SQLAlchemy engine with connection pooling."""
    try:
        # Always use SQLite for reliable local development
        engine = create_engine(SQLITE_URL)
        return engine
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Initialize database schema
def init_db():
    """Initialize database schema if tables don't exist."""
    engine = get_engine()
    if not engine:
        return False
    
    try:
        metadata = MetaData()
        
        # Define contributors table
        contributors = Table(
            'contributors', metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String(100), unique=True, nullable=False),
            Column('first_contribution_date', Date, nullable=False),
            Column('contribution_count', Integer, default=0),
            Column('is_active', Boolean, default=True),
            Column('contribution_type', String(50)),
            Column('email', String(100)),
            Column('display_name', String(100)),
        )
        
        # Define contributions table
        contributions = Table(
            'contributions', metadata,
            Column('id', Integer, primary_key=True),
            Column('contributor_id', Integer, ForeignKey('contributors.id')),
            Column('date', Date, nullable=False),
            Column('type', String(50), nullable=False),  # PR, issue, comment, etc.
            Column('title', String(255)),
            Column('description', Text),
            Column('url', String(255)),
            Column('status', String(50)),  # open, closed, merged, etc.
        )
        
        # Define project_metrics table for time-series data
        project_metrics = Table(
            'project_metrics', metadata,
            Column('id', Integer, primary_key=True),
            Column('date', Date, nullable=False),
            Column('total_contributors', Integer),
            Column('active_contributors', Integer),
            Column('open_issues', Integer),
            Column('closed_issues', Integer),
            Column('open_prs', Integer),
            Column('merged_prs', Integer),
            Column('stars', Integer),
            Column('forks', Integer),
        )
        
        # Define project settings table
        project_settings = Table(
            'project_settings', metadata,
            Column('id', Integer, primary_key=True),
            Column('key', String(100), unique=True, nullable=False),
            Column('value', Text),
            Column('updated_at', Date, default=datetime.now().date())
        )
        
        # Create tables if they don't exist
        metadata.create_all(engine)
        
        # Insert default project settings if they don't exist
        with engine.connect() as conn:
            # Check if project_name exists
            result = conn.execute(text("SELECT COUNT(*) FROM project_settings WHERE key = 'project_name'"))
            if result.scalar() == 0:
                conn.execute(text("INSERT INTO project_settings (key, value) VALUES ('project_name', 'Open Source Project')"))
                
            # Check if project_description exists  
            result = conn.execute(text("SELECT COUNT(*) FROM project_settings WHERE key = 'project_description'"))
            if result.scalar() == 0:
                conn.execute(text("INSERT INTO project_settings (key, value) VALUES ('project_description', 'An amazing open source project')"))
                
            # Check if project_repo exists
            result = conn.execute(text("SELECT COUNT(*) FROM project_settings WHERE key = 'project_repo'"))
            if result.scalar() == 0:
                conn.execute(text("INSERT INTO project_settings (key, value) VALUES ('project_repo', 'https://github.com/organization/repo')"))
                
            # Check if current_contributors exists
            result = conn.execute(text("SELECT COUNT(*) FROM project_settings WHERE key = 'current_contributors'"))
            if result.scalar() == 0:
                conn.execute(text("INSERT INTO project_settings (key, value) VALUES ('current_contributors', '10')"))
                
            # Check if target_contributors exists
            result = conn.execute(text("SELECT COUNT(*) FROM project_settings WHERE key = 'target_contributors'"))
            if result.scalar() == 0:
                conn.execute(text("INSERT INTO project_settings (key, value) VALUES ('target_contributors', '50')"))
                
            conn.commit()
        return True
        
    except Exception as e:
        st.error(f"Error initializing database: {e}")
        return False

# Database operations
def get_contributor_data_from_db():
    """Get contributor data from database."""
    engine = get_engine()
    if not engine:
        from data.sample_metrics import get_sample_contributor_stats
        return get_sample_contributor_stats()
    
    try:
        # Use project_metrics table which already has the dates and contributor counts
        # This is more compatible with SQLite which doesn't support generate_series
        sql_query = """
        SELECT 
            date,
            total_contributors AS cumulative_contributors
        FROM 
            project_metrics
        ORDER BY 
            date;
        """
        
        df = pd.read_sql(sql_query, engine)
        if not df.empty:
            return df
        else:
            # If no data, return sample data
            from data.sample_metrics import get_sample_contributor_stats
            return get_sample_contributor_stats()
    
    except Exception as e:
        st.error(f"Database query error: {e}")
        from data.sample_metrics import get_sample_contributor_stats
        return get_sample_contributor_stats()

def get_activity_data_from_db(days=30):
    """Get repository activity data from database."""
    engine = get_engine()
    if not engine:
        from data.sample_metrics import get_sample_repo_activity
        return get_sample_repo_activity(days)
    
    try:
        # Calculate start date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query to get daily activity from project_metrics
        # This is more compatible with SQLite which doesn't support generate_series
        sql_query = """
        SELECT 
            date,
            open_prs + merged_prs AS pull_requests,
            open_issues + closed_issues AS issues,
            (open_prs + merged_prs + open_issues + closed_issues) * 2 AS comments,
            open_prs + merged_prs + open_issues + closed_issues + 
            ((open_prs + merged_prs + open_issues + closed_issues) * 2) AS total_activity
        FROM 
            project_metrics
        WHERE 
            date BETWEEN ? AND ?
        ORDER BY 
            date;
        """
        
        # Use named parameters for broader database compatibility
        sql_query_named = """
        SELECT 
            date,
            open_prs + merged_prs AS pull_requests,
            open_issues + closed_issues AS issues,
            (open_prs + merged_prs + open_issues + closed_issues) * 2 AS comments,
            open_prs + merged_prs + open_issues + closed_issues + 
            ((open_prs + merged_prs + open_issues + closed_issues) * 2) AS total_activity
        FROM 
            project_metrics
        WHERE 
            date BETWEEN :start_date AND :end_date
        ORDER BY 
            date;
        """
        params = {
            'start_date': start_date.date(),
            'end_date': end_date.date()
        }
        df = pd.read_sql(sql_query_named, engine, params=params)
        if not df.empty:
            return df
        else:
            # If no data, return sample data
            from data.sample_metrics import get_sample_repo_activity
            return get_sample_repo_activity(days)
    
    except Exception as e:
        st.error(f"Database query error: {e}")
        from data.sample_metrics import get_sample_repo_activity
        return get_sample_repo_activity(days)

def get_contribution_types_from_db():
    """Get breakdown of contributor types from database."""
    engine = get_engine()
    if not engine:
        return {
            'code': 65,
            'documentation': 15,
            'design': 5,
            'testing': 10,
            'community': 5
        }
    
    try:
        sql_query = """
        SELECT 
            COALESCE(contribution_type, 'code') AS type,
            COUNT(*) AS count
        FROM 
            contributors
        GROUP BY 
            COALESCE(contribution_type, 'code');
        """
        
        df = pd.read_sql(sql_query, engine)
        if not df.empty:
            # Convert to percentage
            total = df['count'].sum()
            result = {}
            for _, row in df.iterrows():
                result[row['type']] = int((row['count'] / total) * 100)
            return result
        else:
            # If no data, return sample data
            return {
                'code': 65,
                'documentation': 15,
                'design': 5,
                'testing': 10,
                'community': 5
            }
    
    except Exception as e:
        st.error(f"Database query error: {e}")
        return {
            'code': 65,
            'documentation': 15,
            'design': 5,
            'testing': 10,
            'community': 5
        }

def add_contributor(username, first_contribution_date, contribution_type='code', email=None, display_name=None):
    """Add a new contributor to the database."""
    engine = get_engine()
    if not engine:
        st.error("Cannot add contributor: No database connection.")
        return False
    
    try:
        sql_query = text("""
        INSERT INTO contributors 
            (username, first_contribution_date, contribution_count, contribution_type, email, display_name)
        VALUES 
            (:username, :date, 1, :contribution_type, :email, :display_name)
        ON CONFLICT (username) 
        DO UPDATE SET 
            contribution_count = contributors.contribution_count + 1
        RETURNING id
        """)
        
        with engine.connect() as conn:
            result = conn.execute(
                sql_query,
                {
                    "username": username,
                    "date": first_contribution_date,
                    "contribution_type": contribution_type,
                    "email": email or "",
                    "display_name": display_name or ""
                }
            )
            conn.commit()
            
        return True
    
    except Exception as e:
        st.error(f"Error adding contributor: {e}")
        return False

def add_contribution(contributor_username, date, contribution_type, title=None, description=None, url=None, status='open'):
    """Add a new contribution to the database."""
    engine = get_engine()
    if not engine:
        st.error("Cannot add contribution: No database connection.")
        return False
    
    try:
        with engine.connect() as conn:
            # First check if the contributor exists
            get_id_query = text(f"SELECT id FROM contributors WHERE username = :username")
            result = conn.execute(get_id_query, {"username": contributor_username})
            contributor_row = result.fetchone()
            
            # If contributor doesn't exist, create them
            if not contributor_row:
                # Add the contributor
                add_contributor_query = text("""
                INSERT INTO contributors 
                    (username, first_contribution_date, contribution_count, contribution_type)
                VALUES 
                    (:username, :date, 1, 'code')
                RETURNING id
                """)
                
                result = conn.execute(
                    add_contributor_query, 
                    {"username": contributor_username, "date": date}
                )
                conn.commit()
                contributor_row = result.fetchone()
                
                if not contributor_row:
                    raise ValueError(f"Failed to create contributor: {contributor_username}")
            
            contributor_id = contributor_row[0]
            
            # Now add the contribution
            add_contribution_query = text("""
            INSERT INTO contributions 
                (contributor_id, date, type, title, description, url, status)
            VALUES 
                (:contributor_id, :date, :type, :title, :description, :url, :status)
            """)
            
            conn.execute(
                add_contribution_query, 
                {
                    "contributor_id": contributor_id,
                    "date": date,
                    "type": contribution_type,
                    "title": title or "",
                    "description": description or "",
                    "url": url or "",
                    "status": status
                }
            )
            conn.commit()
            
        return True
    
    except Exception as e:
        st.error(f"Error adding contribution: {e}")
        return False

def update_project_metrics(date, metrics_data):
    """Update or insert project metrics for a specific date."""
    engine = get_engine()
    if not engine:
        st.error("Cannot update metrics: No database connection.")
        return False
    
    try:
        # Since we need to build the query dynamically based on provided fields,
        # we'll construct separate parts
        
        # For fields present in metrics_data
        columns = list(metrics_data.keys())
        placeholders = [f":{col}" for col in columns]
        
        # Create the parameter dictionary with the date
        params = {"date": date}
        # Add all the metrics data
        params.update(metrics_data)
        
        # Build the update part dynamically
        update_parts = [f"{col} = :{col}" for col in columns]
        update_clause = ", ".join(update_parts)
        
        # Build the complete query
        query_text = f"""
        INSERT INTO project_metrics 
            (date, {', '.join(columns)})
        VALUES 
            (:date, {', '.join(placeholders)})
        ON CONFLICT (date) 
        DO UPDATE SET 
            {update_clause};
        """
        
        with engine.connect() as conn:
            conn.execute(text(query_text), params)
            conn.commit()
            
        return True
    
    except Exception as e:
        st.error(f"Error updating project metrics: {e}")
        return False

# Test database connection
def test_database_connection():
    """Test if the database connection is working properly."""
    engine = get_engine()
    if not engine:
        return {
            "success": False,
            "message": "No database connection configured."
        }
    
    try:
        # Try a simple query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.fetchone():
                return {
                    "success": True,
                    "message": "Database connection successful."
                }
    except Exception as e:
        return {
            "success": False,
            "message": f"Database connection error: {str(e)}"
        }

# Initialize the database when this module is imported
init_db()

# Get project settings from database
def get_project_settings():
    """Get project settings from database."""
    engine = get_engine()
    project_name = "Open Source Project"
    project_description = "An amazing open source project"
    current_contributors = 10
    target_contributors = 50
    
    if engine:
        try:
            # Get project name
            query = "SELECT value FROM project_settings WHERE key = 'project_name';"
            df = pd.read_sql(query, engine)
            if not df.empty:
                project_name = df.iloc[0]['value']
                
            # Get project description
            query = "SELECT value FROM project_settings WHERE key = 'project_description';"
            df = pd.read_sql(query, engine)
            if not df.empty:
                project_description = df.iloc[0]['value']
                
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
    
    return project_name, project_description, current_contributors, target_contributors

# Print database connection test result
test_result = test_database_connection()
if test_result:
    print(f"Database connection test: {test_result['message']}")