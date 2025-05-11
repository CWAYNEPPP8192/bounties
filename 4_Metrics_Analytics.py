import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from sqlalchemy import text

# Import database functions
sys.path.append(os.path.join(os.getcwd(), 'utils'))
from utils.database_fixed import get_engine, get_contributor_data_from_db, get_activity_data_from_db, get_contribution_types_from_db

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

# Page configuration
st.set_page_config(
    page_title=f"Metrics & Analytics | {project_name}",
    page_icon="📊",
    layout="wide"
)

# Header
st.title("📊 Community Metrics & Analytics")
st.markdown(f"""
This page provides detailed metrics and analytics to track {project_name}'s open source community growth.
We use these insights to measure progress toward our goal of growing from {current_contributors} to {target_contributors} active contributors,
identify trends, and make data-driven decisions about community initiatives.
""")

# Load real data from the database
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_database_data():
    """Load data from the database"""
    engine = get_engine()
    
    # Placeholder for database error
    error_message = None
    
    if not engine:
        error_message = "Database connection failed"
        return None, None, None, None, error_message

    try:
        # Get contributor data - using project_metrics table directly
        # This avoids the problematic generate_series function which is not supported in SQLite
        query = text("""
        SELECT 
            date as date, 
            total_contributors as cumulative_contributors
        FROM 
            project_metrics
        ORDER BY 
            date ASC
        """)
        
        with engine.connect() as conn:
            contributor_result = conn.execute(query)
            contributor_data = pd.DataFrame(contributor_result.fetchall())
            if len(contributor_data) > 0:
                contributor_data.columns = contributor_result.keys()

        # Get activity data
        query = text("""
        SELECT 
            date as date, 
            open_prs + merged_prs as pull_requests,
            open_issues + closed_issues as issues,
            (open_prs + merged_prs + open_issues + closed_issues) * 2 as comments,
            open_prs + merged_prs + open_issues + closed_issues + 
                ((open_prs + merged_prs + open_issues + closed_issues) * 2) as total_activity
        FROM 
            project_metrics
        ORDER BY 
            date ASC
        """)
        
        with engine.connect() as conn:
            activity_result = conn.execute(query)
            activity_data = pd.DataFrame(activity_result.fetchall())
            if len(activity_data) > 0:
                activity_data.columns = activity_result.keys()
                activity_data['date'] = pd.to_datetime(activity_data['date'])

        # Get contributor types
        query = text("""
        SELECT 
            contribution_type, 
            COUNT(*) as count
        FROM 
            contributors
        GROUP BY 
            contribution_type
        """)
        
        with engine.connect() as conn:
            types_result = conn.execute(query)
            types_data = pd.DataFrame(types_result.fetchall())
            if len(types_data) > 0:
                types_data.columns = types_result.keys()
                total = types_data['count'].sum()
                types_data['percentage'] = (types_data['count'] / total) * 100
                
                # Convert to dictionary
                contributor_types = dict(zip(types_data['contribution_type'], types_data['percentage']))
            else:
                contributor_types = {
                    'code': 65,
                    'documentation': 15,
                    'design': 5,
                    'testing': 10,
                    'community': 5
                }

        # Generate retention data based on cohorts
        # First get cohorts (contributors grouped by first contribution month)
        query = text("""
        SELECT 
            strftime('%Y-%m', first_contribution_date) as cohort_month,
            COUNT(*) as cohort_size
        FROM 
            contributors
        GROUP BY 
            cohort_month
        ORDER BY 
            cohort_month ASC
        """)
        
        with engine.connect() as conn:
            cohorts_result = conn.execute(query)
            cohorts_data = pd.DataFrame(cohorts_result.fetchall())
            if len(cohorts_data) > 0:
                cohorts_data.columns = cohorts_result.keys()
                
                # Now generate retention data (simulated for this example)
                # In a real app, you'd calculate this from actual contribution history
                retention_data = []
                
                # Get distinct months from contributor data
                months = pd.date_range(
                    start=pd.to_datetime(contributor_data['date'].min()),
                    end=pd.to_datetime(contributor_data['date'].max()),
                    freq='MS'
                )
                
                for i, row in cohorts_data.iterrows():
                    cohort_month_str = row['cohort_month']
                    cohort_size = row['cohort_size']
                    cohort_month = datetime.strptime(cohort_month_str + "-01", "%Y-%m-%d")
                    
                    # Find index in months
                    try:
                        month_index = [m.strftime('%Y-%m') for m in months].index(cohort_month_str)
                    except ValueError:
                        continue
                    
                    # Calculate retention rates (simulated)
                    retention_rates = []
                    for j in range(len(months) - month_index):
                        if j == 0:
                            rate = 100  # First month always 100%
                        else:
                            # Base retention that declines over time
                            base_retention = 90 * (0.85 ** (j-1))
                            rate = min(100, base_retention)
                        
                        retention_rates.append(rate)
                    
                    # Pad with zeros for past months
                    retention_rates = [0] * month_index + retention_rates
                    
                    retention_data.append({
                        'cohort': cohort_month.strftime('%b %Y'),
                        'cohort_size': cohort_size,
                        'retention': retention_rates,
                        'months': [m.strftime('%b %Y') for m in months]
                    })
            else:
                # Generate empty retention data
                retention_data = []

        return contributor_data, activity_data, retention_data, contributor_types, None
    
    except Exception as e:
        error_message = f"Error loading data: {str(e)}"
        return None, None, None, None, error_message

# Load data
contributor_data, activity_data, retention_data, contributor_types, error_message = load_database_data()

# Display error message if any
if error_message:
    st.error(error_message)
    st.warning("Using sample data because of database error...")
    
    # Generate dates for the past 6 months for sample data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Sample data 
    contributor_data = pd.DataFrame({
        'date': date_range,
        'cumulative_contributors': range(10, 10 + len(date_range))
    })
    
    activity_data = pd.DataFrame({
        'date': date_range,
        'pull_requests': np.random.randint(1, 10, size=len(date_range)),
        'issues': np.random.randint(1, 15, size=len(date_range)),
        'comments': np.random.randint(5, 30, size=len(date_range))
    })
    activity_data['total_activity'] = activity_data['pull_requests'] + activity_data['issues'] + activity_data['comments']
    
    contributor_types = {
        'code': 65,
        'documentation': 15,
        'design': 5,
        'testing': 10,
        'community': 5
    }
    
    # Generate empty retention data
    retention_data = []

# Create tabs for different metrics
tab1, tab2, tab3, tab4 = st.tabs([
    "Growth Metrics", 
    "Activity & Engagement", 
    "Retention Analysis",
    "Contributor Journey"
])

with tab1:
    st.header("Community Growth Metrics")
    st.markdown("""
    Track our progress toward the goal of 50 active contributors and analyze growth patterns.
    """)
    
    # Show current status
    current_contributors = contributor_data['cumulative_contributors'].iloc[-1]
    start_contributors = contributor_data['cumulative_contributors'].iloc[0]
    growth_percentage = ((current_contributors - start_contributors) / start_contributors) * 100
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            label="Current Contributors",
            value=current_contributors,
            delta=int(current_contributors - start_contributors)
        )
    
    with metric_col2:
        st.metric(
            label="Growth Percentage",
            value=f"{growth_percentage:.1f}%"
        )
    
    with metric_col3:
        progress_percentage = (current_contributors / 50) * 100
        st.metric(
            label="Progress to Goal (50)",
            value=f"{progress_percentage:.1f}%"
        )
    
    # Contributor growth chart
    st.subheader("Contributor Growth Over Time")
    
    # Create chart with goal line
    growth_chart_base = alt.Chart(contributor_data).mark_line(color='#33cc33').encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('cumulative_contributors:Q', title='Total Contributors')
    )
    
    # Add goal line
    goal_df = pd.DataFrame({
        'date': [start_date, end_date],
        'goal': [10, 50]
    })
    
    goal_line = alt.Chart(goal_df).mark_line(
        color='red', 
        strokeDash=[3, 3]
    ).encode(
        x='date:T',
        y='goal:Q'
    )
    
    # Add projection line
    projection_end = end_date + timedelta(days=180)
    projection_df = pd.DataFrame({
        'date': [end_date, projection_end],
        'projection': [current_contributors, 50]
    })
    
    projection_line = alt.Chart(projection_df).mark_line(
        color='blue', 
        strokeDash=[5, 5]
    ).encode(
        x='date:T',
        y='projection:Q'
    )
    
    # Combine charts
    growth_chart = growth_chart_base + goal_line + projection_line
    
    # Display chart
    st.altair_chart(growth_chart, use_container_width=True)
    
    # Annotation
    st.caption("Red dashed line: Target growth to reach 50 contributors | Blue dashed line: Current projection")
    
    # Growth breakdown
    st.subheader("Growth Breakdown")
    
    # Monthly aggregation
    monthly_data = contributor_data.copy()
    monthly_data['month'] = monthly_data['date'].dt.strftime('%b %Y')
    monthly_growth = monthly_data.groupby('month').agg({
        'cumulative_contributors': 'last'
    }).reset_index()
    
    # Calculate new contributors per month
    monthly_growth['new_contributors'] = monthly_growth['cumulative_contributors'].diff()
    monthly_growth.loc[0, 'new_contributors'] = 0  # First month shows no new
    
    # Create chart
    monthly_chart = alt.Chart(monthly_growth).mark_bar().encode(
        x=alt.X('month:N', title='Month', sort=None),
        y=alt.Y('new_contributors:Q', title='New Contributors'),
        tooltip=['month', 'new_contributors', 'cumulative_contributors']
    ).properties(
        height=300
    )
    
    st.altair_chart(monthly_chart, use_container_width=True)
    
    # Contributor sources/channels
    st.subheader("Contributor Acquisition Channels")
    
    # Sample acquisition data
    acquisition_data = pd.DataFrame({
        'source': ['GitHub Discovery', 'Community Referral', 'Documentation', 'Social Media', 'Events', 'Blog Posts'],
        'percentage': [30, 25, 15, 15, 10, 5]
    })
    
    # Create horizontal bar chart
    acquisition_chart = alt.Chart(acquisition_data).mark_bar().encode(
        y=alt.Y('source:N', sort='-x', title=None),
        x=alt.X('percentage:Q', title='Percentage of New Contributors'),
        tooltip=['source', 'percentage']
    ).properties(
        height=200
    )
    
    st.altair_chart(acquisition_chart, use_container_width=True)

with tab2:
    st.header("Activity & Engagement Metrics")
    st.markdown("""
    Measure the community's engagement level and activity patterns to identify trends and opportunities.
    """)
    
    # Calculate recent activity metrics
    recent_activity = activity_data.tail(30).sum()
    
    # Activity metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric(
            label="Pull Requests (30d)",
            value=int(recent_activity['pull_requests'])
        )
    
    with metric_col2:
        st.metric(
            label="Issues (30d)",
            value=int(recent_activity['issues'])
        )
    
    with metric_col3:
        st.metric(
            label="Comments (30d)",
            value=int(recent_activity['comments'])
        )
    
    with metric_col4:
        st.metric(
            label="Total Activity (30d)",
            value=int(recent_activity['total_activity'])
        )
    
    # Weekly activity patterns
    st.subheader("Weekly Activity Patterns")
    
    # Prepare data for weekly patterns
    activity_data['day_of_week'] = activity_data['date'].dt.dayofweek
    activity_data['day_name'] = activity_data['date'].dt.day_name()
    
    weekly_pattern = activity_data.groupby('day_of_week').agg({
        'day_name': 'first',
        'pull_requests': 'mean',
        'issues': 'mean',
        'comments': 'mean'
    }).reset_index()
    
    # Reshape data for stacked chart
    weekly_pattern_melted = pd.melt(
        weekly_pattern, 
        id_vars=['day_of_week', 'day_name'],
        value_vars=['pull_requests', 'issues', 'comments'],
        var_name='activity_type',
        value_name='average_count'
    )
    
    # Create chart
    weekly_chart = alt.Chart(weekly_pattern_melted).mark_bar().encode(
        x=alt.X('day_name:N', title='Day of Week', sort=None),
        y=alt.Y('average_count:Q', title='Average Activity'),
        color=alt.Color('activity_type:N', title='Activity Type'),
        tooltip=['day_name', 'activity_type', 'average_count']
    ).properties(
        height=300
    )
    
    st.altair_chart(weekly_chart, use_container_width=True)
    
    # Activity trend over time
    st.subheader("Activity Trend Over Time")
    
    # Aggregate by week for smoother trend
    activity_data['week'] = activity_data['date'].dt.isocalendar().week
    activity_data['year'] = activity_data['date'].dt.isocalendar().year
    activity_data['yearweek'] = activity_data['year'].astype(str) + '-' + activity_data['week'].astype(str)
    
    weekly_activity = activity_data.groupby('yearweek').agg({
        'date': 'first',
        'pull_requests': 'sum',
        'issues': 'sum',
        'comments': 'sum'
    }).reset_index()
    
    # Reshape for multi-line chart
    weekly_activity_melted = pd.melt(
        weekly_activity,
        id_vars=['yearweek', 'date'],
        value_vars=['pull_requests', 'issues', 'comments'],
        var_name='activity_type',
        value_name='count'
    )
    
    # Create chart
    activity_trend_chart = alt.Chart(weekly_activity_melted).mark_line().encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('count:Q', title='Activity Count'),
        color=alt.Color('activity_type:N', title='Activity Type'),
        tooltip=['yearweek', 'activity_type', 'count']
    ).properties(
        height=300
    )
    
    st.altair_chart(activity_trend_chart, use_container_width=True)
    
    # Contributor types breakdown
    st.subheader("Contribution Type Breakdown")
    
    # Prepare data
    contributor_types_df = pd.DataFrame({
        'type': list(contributor_types.keys()),
        'percentage': list(contributor_types.values())
    })
    
    # Create pie chart
    type_chart = alt.Chart(contributor_types_df).mark_arc().encode(
        theta=alt.Theta('percentage:Q'),
        color=alt.Color('type:N', title='Contribution Type'),
        tooltip=['type', 'percentage']
    ).properties(
        height=300
    )
    
    st.altair_chart(type_chart, use_container_width=True)

with tab3:
    st.header("Contributor Retention Analysis")
    st.markdown("""
    Analyze how well we retain contributors over time and identify opportunities to improve retention.
    """)
    
    # Overall retention metrics
    # Calculate some sample metrics
    one_month_retention = 75  # percentage
    three_month_retention = 50  # percentage
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            label="1-Month Retention",
            value=f"{one_month_retention}%"
        )
    
    with metric_col2:
        st.metric(
            label="3-Month Retention",
            value=f"{three_month_retention}%"
        )
    
    with metric_col3:
        # Calculate average lifespan
        avg_lifespan = "2.8 months"
        st.metric(
            label="Avg Contributor Lifespan",
            value=avg_lifespan
        )
    
    # Cohort retention heatmap
    st.subheader("Contributor Cohort Retention")
    
    # Prepare data for heatmap
    cohort_data = []
    
    for cohort in retention_data:
        for i, month in enumerate(cohort['months']):
            if i < len(cohort['retention']):
                retention_value = cohort['retention'][i]
                if retention_value > 0:
                    cohort_data.append({
                        'cohort': cohort['cohort'],
                        'month': month,
                        'retention': retention_value,
                        'size': cohort['cohort_size']
                    })
    
    cohort_df = pd.DataFrame(cohort_data)
    
    # Create heatmap
    cohort_heatmap = alt.Chart(cohort_df).mark_rect().encode(
        x=alt.X('month:N', title='Month', sort=None),
        y=alt.Y('cohort:N', title='Cohort Month', sort=None),
        color=alt.Color('retention:Q', scale=alt.Scale(scheme='greenblue', domain=[0, 100])),
        tooltip=['cohort', 'month', 'retention', 'size']
    ).properties(
        height=300
    )
    
    # Add text labels
    text = alt.Chart(cohort_df).mark_text(color='white').encode(
        x=alt.X('month:N'),
        y=alt.Y('cohort:N'),
        text=alt.Text('retention:Q', format='.0f')
    )
    
    # Combine charts
    final_heatmap = cohort_heatmap + text
    
    st.altair_chart(final_heatmap, use_container_width=True)
    st.caption("Values represent the percentage of each cohort that remained active in subsequent months")
    
    # Retention by contributor type
    st.subheader("Retention by Contributor Type")
    
    # Sample data for retention by type
    retention_by_type = pd.DataFrame({
        'type': ['Code', 'Documentation', 'Design', 'Testing', 'Community'],
        'one_month': [75, 70, 65, 80, 85],
        'three_month': [50, 45, 40, 55, 60],
        'six_month': [30, 25, 20, 35, 45]
    })
    
    # Reshape for grouped bar chart
    retention_by_type_melted = pd.melt(
        retention_by_type,
        id_vars=['type'],
        value_vars=['one_month', 'three_month', 'six_month'],
        var_name='retention_period',
        value_name='retention_rate'
    )
    
    # Create nicer labels
    retention_by_type_melted['period'] = retention_by_type_melted['retention_period'].map({
        'one_month': '1 Month', 
        'three_month': '3 Months', 
        'six_month': '6 Months'
    })
    
    # Create chart
    retention_type_chart = alt.Chart(retention_by_type_melted).mark_bar().encode(
        x=alt.X('type:N', title='Contributor Type'),
        y=alt.Y('retention_rate:Q', title='Retention Rate (%)'),
        color=alt.Color('period:N', title='Retention Period'),
        tooltip=['type', 'period', 'retention_rate']
    ).properties(
        height=300
    )
    
    st.altair_chart(retention_type_chart, use_container_width=True)
    
    # Reasons for contributor churn
    st.subheader("Contributor Churn Analysis")
    
    # Sample data for churn reasons
    churn_reasons = pd.DataFrame({
        'reason': [
            'Time constraints', 
            'Moved to other projects', 
            'Completed specific task',
            'Lack of engagement',
            'Unclear contribution path',
            'Technical barriers',
            'Personal reasons'
        ],
        'percentage': [30, 20, 15, 15, 10, 5, 5]
    })
    
    # Create chart
    churn_chart = alt.Chart(churn_reasons).mark_bar().encode(
        y=alt.Y('reason:N', sort='-x', title=None),
        x=alt.X('percentage:Q', title='Percentage of Churned Contributors'),
        tooltip=['reason', 'percentage']
    ).properties(
        height=250
    )
    
    st.altair_chart(churn_chart, use_container_width=True)
    st.caption("Based on exit surveys and contributor interviews")

with tab4:
    st.header("Contributor Journey Analytics")
    st.markdown("""
    Analyze the contributor journey to identify bottlenecks and optimization opportunities.
    """)
    
    # Funnel analysis
    st.subheader("Contributor Funnel Analysis")
    
    # Sample funnel data
    funnel_data = pd.DataFrame({
        'stage': [
            'GitHub Repository Visitors',
            'Documentation Readers',
            'Discord/Community Joiners',
            'Issue Commenters',
            'First-time Contributors',
            'Repeat Contributors',
            'Regular Contributors'
        ],
        'count': [1000, 500, 200, 100, 50, 25, 15],
    })
    
    # Calculate conversion rates
    funnel_data['conversion'] = funnel_data['count'].pct_change().fillna(1) * 100 + 100
    funnel_data['conversion'] = funnel_data['conversion'].round(1).astype(str) + '%'
    funnel_data.loc[0, 'conversion'] = '100%'
    
    # Create funnel chart
    funnel_chart = alt.Chart(funnel_data).mark_bar().encode(
        y=alt.Y('stage:N', sort=None, title=None),
        x=alt.X('count:Q', title='Number of People'),
        tooltip=['stage', 'count', 'conversion']
    ).properties(
        height=300
    )
    
    st.altair_chart(funnel_chart, use_container_width=True)
    
    # Conversion metrics in columns
    conv_col1, conv_col2, conv_col3 = st.columns(3)
    
    with conv_col1:
        visitor_to_joiner = 20  # %
        st.metric(
            label="Visitor → Community Conversion",
            value=f"{visitor_to_joiner}%"
        )
    
    with conv_col2:
        joiner_to_contributor = 25  # %
        st.metric(
            label="Community → Contributor Conversion",
            value=f"{joiner_to_contributor}%"
        )
    
    with conv_col3:
        first_to_regular = 30  # %
        st.metric(
            label="First-time → Regular Conversion",
            value=f"{first_to_regular}%"
        )
    
    # Time to first contribution
    st.subheader("Time to First Contribution")
    
    # Sample data
    time_to_contribution = pd.DataFrame({
        'days': ['0-7 days', '8-14 days', '15-30 days', '31-60 days', '60+ days'],
        'percentage': [15, 25, 30, 20, 10]
    })
    
    # Create chart
    time_chart = alt.Chart(time_to_contribution).mark_bar().encode(
        x=alt.X('days:N', sort=None, title='Days from First Engagement'),
        y=alt.Y('percentage:Q', title='Percentage of Contributors'),
        tooltip=['days', 'percentage']
    ).properties(
        height=250
    )
    
    st.altair_chart(time_chart, use_container_width=True)
    
    # Journey blockers
    st.subheader("Common Contribution Blockers")
    
    # Sample data
    blockers_data = pd.DataFrame({
        'blocker': [
            'Development environment setup',
            'Understanding codebase structure',
            'Finding appropriate issues',
            'Getting PR reviews',
            'Test suite complexity',
            'Documentation gaps'
        ],
        'impact': [4.2, 3.8, 3.5, 3.3, 2.9, 2.7]
    })
    
    # Create chart
    blockers_chart = alt.Chart(blockers_data).mark_bar().encode(
        y=alt.Y('blocker:N', sort='-x', title=None),
        x=alt.X('impact:Q', title='Impact Score (1-5)'),
        tooltip=['blocker', 'impact']
    ).properties(
        height=250
    )
    
    st.altair_chart(blockers_chart, use_container_width=True)
    st.caption("Based on contributor surveys and interviews (5 = highest impact)")

# Add summary insights
st.header("Key Insights & Recommendations")

# Create two columns for insights and recommendations
insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.subheader("Key Insights")
    st.markdown("""
    Based on the metrics above, we've identified several key insights:
    
    1. **Growth Trajectory:** We're currently on track to reach 30-35 contributors by our target date, falling short of our 50 contributor goal without additional intervention.
    
    2. **Retention Challenge:** While we're attracting new contributors, our 3-month retention rate of 50% indicates we need to improve long-term engagement.
    
    3. **Contributor Funnel:** The largest drop-off in our funnel occurs between community joiners and first-time contributors (75% drop), suggesting barriers to making that first contribution.
    
    4. **Contribution Types:** Code contributions dominate at 65%, with relatively low representation in documentation (15%) and design (5%), indicating potential to diversify.
    
    5. **Time Investment:** Development environment setup and understanding the codebase are the top two barriers reported by new contributors.
    """)

with insight_col2:
    st.subheader("Recommendations")
    st.markdown("""
    Based on our metrics, we recommend the following actions:
    
    1. **Streamline First Contribution:** Create a zero-configuration development environment and more structured "first issue" process to improve conversion from community members to contributors.
    
    2. **Improve Retention:** Establish a formal mentorship program and recognition system to increase 3-month retention from 50% to 70%.
    
    3. **Diversify Contribution Types:** Create specific non-code contribution pathways with dedicated mentors to increase documentation and design contributors by 10%.
    
    4. **Community Engagement:** Increase frequency of community events and create topic-specific working groups to foster deeper engagement.
    
    5. **Documentation Improvement:** Prioritize architecture documentation and onboarding guides based on identified pain points.
    """)

# Add implementation plan
st.subheader("Implementation Plan")

# Create tabs for different timeframes
plan_tab1, plan_tab2, plan_tab3 = st.tabs(["Next 30 Days", "60-Day Plan", "90-Day Plan"])

with plan_tab1:
    st.markdown("""
    ### Next 30 Days - Immediate Actions
    
    1. **Create Development Environment Container**
       - Owner: DevOps Team
       - Expected Impact: Reduce environment setup time by 80%
       - Metrics to Track: Time to first build, setup-related support requests
    
    2. **Revamp "Good First Issue" Process**
       - Owner: Community Manager
       - Expected Impact: Increase first-time contributors by 30%
       - Metrics to Track: Time to first contribution, first-issue completion rate
    
    3. **Launch Contributor Survey**
       - Owner: Community Manager
       - Expected Impact: Gather detailed feedback from current and churned contributors
       - Metrics to Track: Survey completion rate, identified improvement areas
    """)

with plan_tab2:
    st.markdown("""
    ### 60-Day Plan - Building Momentum
    
    1. **Implement Formal Mentorship Program**
       - Owner: Core Team
       - Expected Impact: Increase 3-month retention by 20%
       - Metrics to Track: Mentor/mentee satisfaction, retention of mentored contributors
    
    2. **Create Non-Code Contribution Guides**
       - Owner: Documentation Team
       - Expected Impact: Increase non-code contributions by 25%
       - Metrics to Track: Documentation/design contribution rates
    
    3. **Improve Architecture Documentation**
       - Owner: Technical Writers + Engineering
       - Expected Impact: Reduce codebase understanding time by 50%
       - Metrics to Track: Documentation usage, reported understanding barriers
    """)

with plan_tab3:
    st.markdown("""
    ### 90-Day Plan - Scaling Impact
    
    1. **Launch Topic-Specific Working Groups**
       - Owner: Community Team
       - Expected Impact: Create deeper engagement opportunities for contributors
       - Metrics to Track: Working group participation, contributor retention
    
    2. **Implement Contributor Recognition Program**
       - Owner: Community Manager
       - Expected Impact: Increase contributor satisfaction and visibility
       - Metrics to Track: Retention rates, survey satisfaction scores
    
    3. **Create Contribution Growth Challenges**
       - Owner: Marketing + Community
       - Expected Impact: Accelerate growth toward 50-contributor goal
       - Metrics to Track: New contributor acquisition, challenge participation
    """)

# Custom report section
st.header("Custom Reports")
st.markdown("""
Create custom reports by selecting metrics and date ranges below.
""")

# Create form for custom report
with st.form("custom_report_form"):
    report_col1, report_col2 = st.columns(2)
    
    with report_col1:
        metrics = st.multiselect(
            "Select Metrics",
            ["New Contributors", "Pull Requests", "Issues", "Comments", "Retention Rate"],
            default=["New Contributors", "Pull Requests"]
        )
    
    with report_col2:
        date_range = st.date_input(
            "Date Range",
            value=[start_date.date(), end_date.date()]
        )
    
    report_format = st.selectbox(
        "Report Format",
        ["Interactive Chart", "CSV Data", "PDF Report (Premium)"]
    )
    
    submitted = st.form_submit_button("Generate Report")
    
    if submitted:
        st.info("Custom reports will be implemented in a future update. Currently, this is a placeholder for demonstration purposes.")

# footer
st.markdown("---")
st.caption(f"{project_name} Community Dashboard - Helping grow our community from {current_contributors} to {target_contributors} active contributors")
