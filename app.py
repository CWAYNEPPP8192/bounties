import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Open Source Community Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import the rest of the modules after page config
import pandas as pd
import altair as alt
from utils.github_api import get_contributor_stats
from utils.data_processing import process_contributor_data, calculate_growth_metrics
from utils.visualization import create_progress_chart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database functions after page config
from utils.database_fixed import get_engine, get_contributor_data_from_db, get_activity_data_from_db, get_contribution_types_from_db, get_project_settings

# Get project settings
project_name, project_description, current_contributors, target_contributors = get_project_settings()

# Initialize session state
if 'current_contributors' not in st.session_state:
    st.session_state.current_contributors = current_contributors  # Starting point
if 'target_contributors' not in st.session_state:
    st.session_state.target_contributors = target_contributors  # Goal

# Main dashboard header
st.title(f"🌱 {project_name} Community Dashboard")
st.markdown(f"""
Welcome to the {project_name} Community Dashboard! This platform helps track and grow
our community from {current_contributors} to {target_contributors} active contributors. Use the sidebar to navigate through
different sections of the dashboard.
""")

# Sidebar for navigation
with st.sidebar:
    st.title(f"{project_name} Growth Hub")
    st.markdown("Navigate through the dashboard using the menu above or explore key metrics below.")
    
    # Current status metrics in sidebar
    st.subheader("Community Status")
    current = st.session_state.current_contributors
    target = st.session_state.target_contributors
    progress = current / target
    
    st.metric(
        label="Active Contributors", 
        value=current,
        delta=f"{current - current_contributors} since start"
    )
    
    st.progress(progress)
    st.caption(f"Progress: {current}/{target} contributors ({int(progress*100)}%)")

# Main dashboard content - split into columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Contributor Growth Overview")
    
    # Try to get data from database, fall back to sample data if needed
    try:
        contributor_data = get_contributor_data_from_db()
        # Calculate growth metrics
        growth_metrics = calculate_growth_metrics(contributor_data)
        
        # Set the latest count in session state
        current = int(growth_metrics["current_contributors"])
        st.session_state.current_contributors = current
        
        # Create visualization
        progress_chart = create_progress_chart(current)
        st.altair_chart(progress_chart, use_container_width=True)
        
        # Growth rate indicator
        if growth_metrics["growth_rate"] > 0:
            days_to_goal = int(growth_metrics["days_to_goal"])
            if days_to_goal < float('inf'):
                st.success(f"At the current growth rate, we'll reach our goal of {target} contributors in approximately {days_to_goal} days.")
            else:
                st.info(f"We need to increase our growth rate to reach our goal of {target} contributors.")
    except Exception as e:
        st.error(f"Error loading contributor data: {e}")
        # Fallback to default chart
        progress_chart = create_progress_chart(current)
        st.altair_chart(progress_chart, use_container_width=True)
    
    # Key metrics
    st.subheader("Key Community Metrics")
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    # Try to get activity data
    try:
        activity_data = get_activity_data_from_db(days=30)
        recent_prs = int(activity_data['pull_requests'].sum())
        recent_issues = int(activity_data['issues'].sum())
        
        with metric_col1:
            new_contributors = max(0, current - 10)  # Assuming started with 10
            st.metric(label="New Contributors (Total)", value=str(new_contributors))
        with metric_col2:
            st.metric(label="Recent Pull Requests (30d)", value=str(recent_prs))
        with metric_col3:
            st.metric(label="Recent Issues (30d)", value=str(recent_issues))
    except Exception as e:
        # Fallback to sample data
        with metric_col1:
            st.metric(label="New Contributors (Last Month)", value="3")
        with metric_col2:
            st.metric(label="Open Pull Requests", value="12")
        with metric_col3:
            st.metric(label="Avg Response Time", value="2.3 days")

with col2:
    st.subheader("Quick Actions")
    
    # Action buttons
    st.button("View Beginner Friendly Issues", key="beginner_issues")
    st.button("Find Mentoring Opportunities", key="mentoring")
    st.button("Review Contribution Guidelines", key="guidelines")
    
    # Upcoming events/milestones
    st.subheader("Upcoming Milestones")
    st.info("Community Call: First Friday of the month")
    st.info("Hacktoberfest Participation: October 2023")
    st.info("Next Target: 15 contributors by Q3 2023")

# Community engagement features 
st.subheader("Recent Community Activity")
with st.container():
    tab1, tab2, tab3 = st.tabs(["Recent Contributions", "Discussions", "Recognition"])
    
    with tab1:
        st.markdown("""
        | Contributor | Contribution | Date |
        |-------------|--------------|------|
        | @developer1 | Fixed documentation links | Yesterday |
        | @developer2 | Added new tests for auth module | 2 days ago |
        | @developer3 | Improved error handling in API | Last week |
        """)
    
    with tab2:
        st.markdown("""
        - **Architecture Discussion:** Evaluating new storage options
        - **Feature Request:** Improved user onboarding experience
        - **Community Request:** More beginner-friendly issues
        """)
    
    with tab3:
        st.markdown("""
        🏆 **Contributor of the Month:** @developer2  
        🌟 **First-time Contributor:** @newdev1, @newdev2  
        💯 **Most Active Reviewer:** @seniordev1
        """)

# Call to action
st.subheader("Ready to Contribute?")
st.markdown(f"""
{project_name} is growing its open-source community and we'd love your help! Whether you're a 
seasoned developer or just getting started, there are ways for you to contribute.

Check out the [Community Resources](Community_Resources) page to learn how to get started.
""")

# footer
st.markdown("---")
st.caption(f"{project_name} Community Dashboard - Helping grow our community from {current_contributors} to {target_contributors} active contributors")
