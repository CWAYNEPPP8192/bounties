import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import numpy as np

def create_progress_chart(current_contributors, target=50, start=10):
    """
    Create a progress chart showing growth toward contributor goal.
    
    Args:
        current_contributors (int): Current number of contributors
        target (int): Target number of contributors (default 50)
        start (int): Starting number of contributors (default 10)
        
    Returns:
        altair.Chart: Progress chart visualization
    """
    # Calculate progress percentage
    progress = (current_contributors - start) / (target - start)
    progress_pct = min(1.0, max(0.0, progress))
    
    # Create sample data points for trend visualization
    days_passed = 90  # Assuming 90 days have passed in the campaign
    
    # Generate dates from 90 days ago until 90 days in the future
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_passed)
    future_date = end_date + timedelta(days=90)
    date_range = pd.date_range(start=start_date, end=future_date, freq='D')
    
    # Create a smooth growth curve for past data
    past_dates = date_range[date_range <= end_date]
    past_count = np.linspace(start, current_contributors, len(past_dates))
    past_data = pd.DataFrame({
        'date': past_dates,
        'contributors': past_count,
        'type': 'Actual'
    })
    
    # Create projected data
    future_dates = date_range[date_range > end_date]
    
    # If growth is on track, project to hit target in 90 more days
    # Otherwise, project based on current growth rate
    if progress >= days_passed / (days_passed + 90):
        # On track or ahead of schedule
        future_count = np.linspace(
            current_contributors, 
            target, 
            len(future_dates) + 1
        )[1:]
    else:
        # Behind schedule - project based on current rate
        growth_rate = (current_contributors - start) / days_passed
        future_count = np.array([
            min(target, current_contributors + growth_rate * (i + 1)) 
            for i in range(len(future_dates))
        ])
    
    future_data = pd.DataFrame({
        'date': future_dates,
        'contributors': future_count,
        'type': 'Projected'
    })
    
    # Combine past and future data
    chart_data = pd.concat([past_data, future_data])
    
    # Create target reference line data
    target_data = pd.DataFrame({
        'date': [start_date, future_date],
        'target': [target, target]
    })
    
    # Create ideal progress line data
    ideal_data = pd.DataFrame({
        'date': [start_date, future_date],
        'ideal': [start, target]
    })
    
    # Create the chart
    base_chart = alt.Chart(chart_data).mark_line().encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('contributors:Q', title='Contributors', scale=alt.Scale(domain=[0, target * 1.1])),
        color=alt.Color('type:N', legend=alt.Legend(title=''))
    )
    
    # Add target reference line
    target_line = alt.Chart(target_data).mark_line(
        strokeDash=[4, 4],
        color='red'
    ).encode(
        x='date:T',
        y='target:Q'
    )
    
    # Add ideal progress line
    ideal_line = alt.Chart(ideal_data).mark_line(
        strokeDash=[2, 2],
        color='gray'
    ).encode(
        x='date:T',
        y='ideal:Q'
    )
    
    # Combine the charts
    final_chart = alt.layer(
        base_chart, target_line, ideal_line
    ).properties(
        height=300
    )
    
    return final_chart

def create_retention_heatmap(retention_data):
    """
    Create a cohort retention heatmap visualization.
    
    Args:
        retention_data (list): List of cohort retention data
        
    Returns:
        altair.Chart: Retention heatmap visualization
    """
    # Flatten retention data for visualization
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
    
    # Convert to DataFrame
    if not cohort_data:
        return alt.Chart().mark_rect()
    
    cohort_df = pd.DataFrame(cohort_data)
    
    # Create heatmap
    heatmap = alt.Chart(cohort_df).mark_rect().encode(
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
    final_heatmap = heatmap + text
    
    return final_heatmap

def create_activity_chart(activity_data):
    """
    Create a stacked area chart of daily activity.
    
    Args:
        activity_data (pandas.DataFrame): DataFrame with daily activity counts
        
    Returns:
        altair.Chart: Activity visualization
    """
    if activity_data is None or activity_data.empty:
        return alt.Chart().mark_area()
    
    # Reshape data for stacked area chart
    melted_data = pd.melt(
        activity_data,
        id_vars=['date'],
        value_vars=['pull_requests', 'issues', 'comments'],
        var_name='activity_type',
        value_name='count'
    )
    
    # Create friendlier labels
    activity_labels = {
        'pull_requests': 'Pull Requests',
        'issues': 'Issues',
        'comments': 'Comments'
    }
    
    melted_data['activity'] = melted_data['activity_type'].map(activity_labels)
    
    # Create chart
    activity_chart = alt.Chart(melted_data).mark_area().encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('count:Q', title='Activity Count', stack='zero'),
        color=alt.Color('activity:N', scale=alt.Scale(scheme='category10'), legend=alt.Legend(title='Activity Type')),
        tooltip=['date', 'activity', 'count']
    ).properties(
        height=300
    )
    
    return activity_chart

def create_contributor_type_chart(contributor_types):
    """
    Create a pie chart showing distribution of contributor types.
    
    Args:
        contributor_types (dict): Dictionary mapping contribution types to percentages
        
    Returns:
        altair.Chart: Pie chart visualization
    """
    if not contributor_types:
        return alt.Chart().mark_arc()
    
    # Convert dictionary to DataFrame
    type_data = pd.DataFrame({
        'type': list(contributor_types.keys()),
        'percentage': list(contributor_types.values())
    })
    
    # Create pie chart
    pie_chart = alt.Chart(type_data).mark_arc().encode(
        theta=alt.Theta('percentage:Q'),
        color=alt.Color('type:N', scale=alt.Scale(scheme='category10'), legend=alt.Legend(title='Contribution Type')),
        tooltip=['type', 'percentage']
    ).properties(
        height=300
    )
    
    return pie_chart

def create_funnel_chart(funnel_data):
    """
    Create a horizontal funnel chart for contributor journey.
    
    Args:
        funnel_data (dict): Dictionary with funnel stage names and values
        
    Returns:
        altair.Chart: Funnel chart visualization
    """
    if not funnel_data:
        return alt.Chart().mark_bar()
    
    # Convert dictionary to DataFrame
    stages = list(funnel_data.keys())
    counts = list(funnel_data.values())
    
    funnel_df = pd.DataFrame({
        'stage': stages,
        'count': counts
    })
    
    # Add conversion rates
    funnel_df['previous'] = funnel_df['count'].shift(1)
    funnel_df['conversion'] = (funnel_df['count'] / funnel_df['previous'] * 100).round(1)
    funnel_df.loc[0, 'conversion'] = 100.0
    funnel_df['conversion_label'] = funnel_df['conversion'].astype(str) + '%'
    
    # Create funnel chart
    funnel_chart = alt.Chart(funnel_df).mark_bar().encode(
        y=alt.Y('stage:N', sort=None, title=None),
        x=alt.X('count:Q', title='Number of People'),
        tooltip=['stage', 'count', 'conversion_label']
    ).properties(
        height=300
    )
    
    return funnel_chart
