import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# This file contains functions that generate sample data for the dashboard
# In a real application, this data would come from the GitHub API or another data source

def get_sample_contributor_stats():
    """
    Generate sample contributor statistics.
    
    Returns:
        pandas.DataFrame: DataFrame with sample contributor growth over time
    """
    # Generate dates for the past 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Start with 10 contributors and grow to current number (between 15-20)
    # with some randomness to make it look realistic
    current_contributors = np.random.randint(15, 21)
    
    # Create a somewhat realistic growth curve
    base_growth = np.linspace(10, current_contributors, len(date_range))
    
    # Add some randomness, but ensure it's monotonically increasing
    noise = np.random.normal(0, 0.5, len(date_range))
    cumulative = np.floor(base_growth + np.cumsum(noise) * 0.1)
    cumulative = np.maximum.accumulate(cumulative)  # Ensure it never decreases
    cumulative[0] = 10  # Start exactly at 10
    cumulative[-1] = current_contributors  # End at the current number
    
    return pd.DataFrame({
        'date': date_range,
        'cumulative_contributors': cumulative.astype(int)
    })

def get_sample_pull_requests(state="all", days=30):
    """
    Generate sample PR data.
    
    Args:
        state (str): State filter (open, closed, all)
        days (int): Number of days to generate data for
        
    Returns:
        pandas.DataFrame: DataFrame with sample PR data
    """
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Create sample data
    prs = []
    
    # Generate between 20-40 PRs
    num_prs = np.random.randint(20, 41)
    
    for i in range(num_prs):
        # Random date within range
        created_date = start_date + timedelta(days=np.random.randint(0, days+1))
        
        # Determine PR state and closed date if applicable
        if state == "open" or (state == "all" and np.random.random() < 0.3):
            pr_state = "open"
            closed_date = None
        else:
            pr_state = "closed"
            # Most PRs are closed within a week
            days_to_close = min(np.random.exponential(5), 30)
            close_date = created_date + timedelta(days=days_to_close)
            closed_date = None if close_date > end_date else close_date
        
        # Skip if doesn't match filter
        if state != "all" and pr_state != state:
            continue
        
        # Determine if first-time contributor
        is_first_time = np.random.random() < 0.2
        
        prs.append({
            "id": i + 1000,
            "title": f"Sample PR #{i+1}",
            "state": pr_state,
            "created_at": created_date,
            "closed_at": closed_date,
            "user": f"user{np.random.randint(1, 30)}",
            "is_first_time_contributor": is_first_time,
            "comments": np.random.randint(0, 10)
        })
    
    return pd.DataFrame(prs)

def get_sample_issues(state="all", days=30):
    """
    Generate sample issue data.
    
    Args:
        state (str): State filter (open, closed, all)
        days (int): Number of days to generate data for
        
    Returns:
        pandas.DataFrame: DataFrame with sample issue data
    """
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Create sample data
    issues = []
    
    # Generate between 30-60 issues
    num_issues = np.random.randint(30, 61)
    
    for i in range(num_issues):
        # Random date within range
        created_date = start_date + timedelta(days=np.random.randint(0, days+1))
        
        # Determine issue state and closed date if applicable
        if state == "open" or (state == "all" and np.random.random() < 0.4):
            issue_state = "open"
            closed_date = None
        else:
            issue_state = "closed"
            # Issues often take longer to close than PRs
            days_to_close = min(np.random.exponential(10), 30)
            close_date = created_date + timedelta(days=days_to_close)
            closed_date = None if close_date > end_date else close_date
        
        # Skip if doesn't match filter
        if state != "all" and issue_state != state:
            continue
        
        # Randomly assign labels
        labels = []
        if np.random.random() < 0.2:
            labels.append("bug")
        if np.random.random() < 0.15:
            labels.append("enhancement")
        if np.random.random() < 0.1:
            labels.append("documentation")
        if np.random.random() < 0.15:
            labels.append("good first issue")
        
        issues.append({
            "id": i + 2000,
            "title": f"Sample Issue #{i+1}",
            "state": issue_state,
            "created_at": created_date,
            "closed_at": closed_date,
            "user": f"user{np.random.randint(1, 40)}",
            "labels": labels,
            "comments": np.random.randint(0, 15)
        })
    
    return pd.DataFrame(issues)

def get_sample_repo_activity(days=30):
    """
    Generate sample daily repository activity.
    
    Args:
        days (int): Number of days to generate data for
        
    Returns:
        pandas.DataFrame: DataFrame with daily activity counts
    """
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create activity data with some patterns:
    # - Higher activity on weekdays
    # - Increasing trend over time
    # - Some randomness
    
    activity_data = []
    
    for date in date_range:
        # Base activity levels
        base_pr = 1.2
        base_issue = 2.0
        base_comment = 5.0
        
        # Day of week effect (higher on weekdays)
        if date.dayofweek < 5:  # Weekday
            day_factor = 1.5
        else:  # Weekend
            day_factor = 0.6
        
        # Time trend (activity increases over time as project grows)
        days_since_start = (date - start_date).days
        trend_factor = 1 + (days_since_start / days) * 0.5
        
        # Add some randomness
        pr_count = max(0, int(np.random.poisson(base_pr * day_factor * trend_factor)))
        issue_count = max(0, int(np.random.poisson(base_issue * day_factor * trend_factor)))
        comment_count = max(0, int(np.random.poisson(base_comment * day_factor * trend_factor)))
        
        activity_data.append({
            "date": date,
            "pull_requests": pr_count,
            "issues": issue_count,
            "comments": comment_count,
            "total_activity": pr_count + issue_count + comment_count
        })
    
    return pd.DataFrame(activity_data)

def get_sample_repo_traffic():
    """
    Generate sample repository traffic statistics.
    
    Returns:
        dict: Dictionary with traffic statistics
    """
    days = 14  # GitHub provides 14 days of traffic data
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate view counts with patterns
    views = []
    visitors = []
    
    for date in date_range:
        # Base traffic
        base_views = 50
        
        # Day of week effect
        if date.dayofweek < 5:  # Weekday
            day_factor = 1.3
        else:  # Weekend
            day_factor = 0.7
        
        # Random variability
        random_factor = np.random.uniform(0.7, 1.3)
        
        # Calculate views and unique visitors
        day_views = int(base_views * day_factor * random_factor)
        day_visitors = int(day_views * np.random.uniform(0.3, 0.6))  # 30-60% of views are unique visitors
        
        views.append(day_views)
        visitors.append(day_visitors)
    
    return {
        "dates": [d.strftime('%Y-%m-%d') for d in date_range],
        "views": views,
        "unique_visitors": visitors,
        "total_views": sum(views),
        "total_visitors": sum(visitors)
    }

def get_sample_community_profile():
    """
    Generate sample community health metrics.
    
    Returns:
        dict: Community health metrics
    """
    return {
        "health_percentage": 80,
        "description": True,
        "documentation": True,
        "code_of_conduct": True,
        "contributing": True,
        "issue_template": True,
        "pull_request_template": False,
        "license": True,
        "readme": True
    }

def get_sample_contributor_retention():
    """
    Generate sample contributor retention data.
    
    Returns:
        list: List of cohort retention data
    """
    # Generate months for cohorts
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    months = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    retention_data = []
    
    for i, month in enumerate(months):
        month_name = month.strftime('%b %Y')
        
        # Calculate cohort size (new contributors that month)
        # More recent months have larger cohorts due to growing project
        base_size = 3 + i // 2
        cohort_size = np.random.randint(base_size - 1, base_size + 2)
        
        # Calculate retention rates with some randomness
        # Earlier cohorts have higher long-term retention due to more committed early adopters
        retention_rates = []
        for j in range(len(months) - i):
            if j == 0:
                rate = 100  # First month always 100%
            else:
                # Base retention that declines over time
                base_retention = 90 * (0.85 ** (j-1))
                
                # Early cohorts retain slightly better
                cohort_factor = 1 + (0.05 * (len(months) - i) / len(months))
                
                # Add some randomness
                random_factor = np.random.uniform(0.9, 1.1)
                
                rate = min(100, base_retention * cohort_factor * random_factor)
            
            retention_rates.append(rate)
        
        # Pad with zeros for future months
        retention_rates.extend([0] * i)
        
        retention_data.append({
            'cohort': month_name,
            'cohort_size': cohort_size,
            'retention': retention_rates,
            'months': [m.strftime('%b %Y') for m in months]
        })
    
    return retention_data
