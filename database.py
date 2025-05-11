import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, MetaData, Table, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

# Get DATABASE_URL from environment variables or use default
DATABASE_URL = os.environ.get('DATABASE_URL')
# If url starts with postgres://, replace with postgresql:// (SQLAlchemy requirement)
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Create database engine
@st.cache_resource
def get_engine():
    """Get SQLAlchemy engine with connection pooling."""
    if not DATABASE_URL:
        st.warning("No database connection configured. Using sample data only.")
        return None
    try:
        engine = create_engine(DATABASE_URL)
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
        
        # Create tables if they don't exist
        metadata.create_all(engine)
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
        # Get data by date to create time series
        query = """
        WITH dates AS (
            SELECT generate_series(
                (SELECT MIN(first_contribution_date) FROM contributors),
                CURRENT_DATE,
                '1 day'::interval
            )::date AS date
        )
        SELECT 
            dates.date,
            COUNT(DISTINCT c.id) AS cumulative_contributors
        FROM 
            dates
        LEFT JOIN 
            contributors c ON c.first_contribution_date <= dates.date
        GROUP BY 
            dates.date
        ORDER BY 
            dates.date;
        """
        
        df = pd.read_sql(query, engine)
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
        
        # Query to get daily activity
        query = f"""
        WITH dates AS (
            SELECT generate_series(
                '{start_date.date()}'::date,
                '{end_date.date()}'::date,
                '1 day'::interval
            )::date AS date
        )
        SELECT 
            dates.date,
            COUNT(CASE WHEN c.type = 'pull_request' THEN 1 END) AS pull_requests,
            COUNT(CASE WHEN c.type = 'issue' THEN 1 END) AS issues,
            COUNT(CASE WHEN c.type = 'comment' THEN 1 END) AS comments,
            COUNT(*) AS total_activity
        FROM 
            dates
        LEFT JOIN 
            contributions c ON c.date = dates.date
        GROUP BY 
            dates.date
        ORDER BY 
            dates.date;
        """
        
        df = pd.read_sql(query, engine)
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
        query = """
        SELECT 
            COALESCE(contribution_type, 'code') AS type,
            COUNT(*) AS count
        FROM 
            contributors
        GROUP BY 
            COALESCE(contribution_type, 'code');
        """
        
        df = pd.read_sql(query, engine)
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
        sql_query = f"""
        INSERT INTO contributors 
            (username, first_contribution_date, contribution_count, contribution_type, email, display_name)
        VALUES 
            ('{username}', '{first_contribution_date}', 1, '{contribution_type}', '{email}', '{display_name}')
        ON CONFLICT (username) 
        DO UPDATE SET 
            contribution_count = contributors.contribution_count + 1
        RETURNING id;
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
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
        # First get the contributor_id
        get_id_query = f"""
        SELECT id FROM contributors WHERE username = '{contributor_username}';
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(get_id_query))
            contributor_id = result.fetchone()
            
            if not contributor_id:
                # Create new contributor if doesn't exist
                add_contributor(contributor_username, date)
                result = conn.execute(text(get_id_query))
                contributor_id = result.fetchone()
            
            contributor_id = contributor_id[0]
            
            # Insert contribution
            sql_query = f"""
            INSERT INTO contributions 
                (contributor_id, date, type, title, description, url, status)
            VALUES 
                ({contributor_id}, '{date}', '{contribution_type}', '{title}', '{description}', '{url}', '{status}');
            """
            
            conn.execute(text(sql_query))
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
        columns = ', '.join(metrics_data.keys())
        values = ', '.join([str(v) if isinstance(v, (int, float)) else f"'{v}'" for v in metrics_data.values()])
        
        # Build the update clause
        update_clauses = []
        for k, v in metrics_data.items():
            if isinstance(v, (int, float)):
                update_clauses.append(f"{k} = {v}")
            else:
                update_clauses.append(f"{k} = '{v}'")
        
        sql_query = f"""
        INSERT INTO project_metrics 
            (date, {columns})
        VALUES 
            ('{date}', {values})
        ON CONFLICT (date) 
        DO UPDATE SET 
            {', '.join(update_clauses)};
        """
        
        with engine.connect() as conn:
            conn.execute(text(sql_query))
            conn.commit()
            
        return True
    
    except Exception as e:
        st.error(f"Error updating project metrics: {e}")
        return False

# Initialize the database when this module is imported
init_db()