"""
Initialize database with sample data for demonstration purposes.
This script can be run independently to populate the database with realistic sample data.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import random
from sqlalchemy import text
from utils.database_fixed import get_engine, init_db

# GitHub usernames for sample data
GITHUB_USERNAMES = [
    "johndoe", "janedoe", "alex_dev", "sarahcoder", "dev_mike", 
    "codemaster", "techguru", "pythonista", "javafan", "webdev", 
    "fullstack_pro", "frontend_wizard", "backend_ninja", "data_scientist",
    "ml_engineer", "cloud_architect", "devops_guru", "security_expert",
    "mobile_dev", "game_developer", "open_source_fan", "code_reviewer",
    "bug_hunter", "feature_builder", "doc_writer", "tester_pro",
    "ui_designer", "ux_specialist", "accessibility_advocate", "performance_tuner"
]

# Contribution types
CONTRIBUTION_TYPES = ["code", "documentation", "design", "testing", "community"]

# PR/Issue titles and descriptions
PR_TITLES = [
    "Fix navigation responsiveness",
    "Add dark mode support",
    "Improve error handling",
    "Update documentation",
    "Optimize database queries",
    "Add unit tests for auth module",
    "Fix typos in README",
    "Implement new feature X",
    "Refactor authentication flow",
    "Add logging throughout app",
    "Fix security vulnerability",
    "Update dependencies",
    "Improve accessibility",
    "Optimize images",
    "Add keyboard shortcuts",
    "Implement search functionality",
    "Fix CSS on mobile devices",
    "Add contributor guidelines"
]

ISSUE_TITLES = [
    "App crashes when logging in",
    "Documentation is outdated",
    "Performance issue on dashboard",
    "Feature request: Add export function",
    "Bug: Form validation fails",
    "Missing accessibility labels",
    "Improve error messages",
    "Add support for dark mode",
    "Request: Better mobile experience",
    "Security concern in auth flow",
    "Typos in user interface",
    "Broken links in documentation",
    "Slow loading on profile page",
    "Enhancement suggestion for UI"
]

def generate_contributor_data(num_contributors=25):
    """Generate realistic contributor data"""
    contributors = []
    
    # Start date (6 months ago)
    start_date = datetime.now() - timedelta(days=180)
    
    # Create a distribution of join dates (more joining recently)
    days_ago = np.random.exponential(scale=60, size=num_contributors).astype(int)
    days_ago = np.clip(days_ago, 0, 180)  # Ensure within 6 months
    
    for i in range(num_contributors):
        # Select a username
        username = GITHUB_USERNAMES[i % len(GITHUB_USERNAMES)]
        
        # Calculate join date
        join_date = datetime.now() - timedelta(days=int(days_ago[i]))
        
        # Determine contribution type with distribution
        weights = [0.65, 0.15, 0.05, 0.1, 0.05]  # Most are code contributors
        contribution_type = random.choices(CONTRIBUTION_TYPES, weights=weights)[0]
        
        # Contribution count based on join date (newer = fewer)
        avg_per_month = random.randint(1, 5)
        months_active = days_ago[i] / 30
        contribution_count = int(avg_per_month * months_active) + 1
        
        # Add some randomness
        contribution_count = max(1, int(contribution_count * random.uniform(0.7, 1.3)))
        
        contributors.append({
            "username": username,
            "first_contribution_date": join_date.date(),
            "contribution_count": contribution_count,
            "is_active": random.random() > 0.2,  # 80% active
            "contribution_type": contribution_type,
            "email": f"{username}@example.com" if random.random() > 0.3 else None,
            "display_name": username.replace("_", " ").title() if random.random() > 0.5 else None
        })
    
    return contributors

def generate_contribution_data(contributors, multiplier=3):
    """Generate realistic contribution data based on contributors"""
    contributions = []
    
    for contributor in contributors:
        username = contributor["username"]
        join_date = contributor["first_contribution_date"]
        count = contributor["contribution_count"]
        
        # Create multiple contributions per contributor
        for i in range(count * multiplier):
            # Determine date (more recent = more likely)
            days_since_join = (datetime.now().date() - join_date).days
            if days_since_join <= 0:
                days_since_join = 1
                
            days_ago = int(random.betavariate(1.5, 5) * days_since_join)
            contrib_date = datetime.now().date() - timedelta(days=days_ago)
            
            # Determine type
            if contributor["contribution_type"] == "code":
                contrib_type = random.choices(
                    ["pull_request", "issue", "comment"],
                    weights=[0.6, 0.3, 0.1]
                )[0]
            elif contributor["contribution_type"] == "documentation":
                contrib_type = random.choices(
                    ["pull_request", "issue", "comment"],
                    weights=[0.7, 0.2, 0.1]
                )[0]
            elif contributor["contribution_type"] == "design":
                contrib_type = random.choices(
                    ["pull_request", "issue"],
                    weights=[0.4, 0.6]
                )[0]
            elif contributor["contribution_type"] == "testing":
                contrib_type = random.choices(
                    ["pull_request", "issue", "comment"],
                    weights=[0.3, 0.6, 0.1]
                )[0]
            else:  # community
                contrib_type = random.choices(
                    ["comment", "issue"],
                    weights=[0.7, 0.3]
                )[0]
            
            # Title and description
            if contrib_type == "pull_request":
                title = random.choice(PR_TITLES)
                description = f"This PR {title.lower()} to improve the project."
            elif contrib_type == "issue":
                title = random.choice(ISSUE_TITLES)
                description = f"I found this issue: {title.lower()}. Please fix it."
            else:  # comment
                title = "Comment on " + random.choice(["PR", "Issue"])
                description = "I think this is a good approach. Let's implement it."
            
            # Status
            if contrib_type == "pull_request":
                status = random.choices(
                    ["open", "merged", "closed"],
                    weights=[0.2, 0.7, 0.1]
                )[0]
            elif contrib_type == "issue":
                status = random.choices(
                    ["open", "closed"],
                    weights=[0.4, 0.6]
                )[0]
            else:  # comment
                status = "posted"
            
            # URL
            url = f"https://github.com/gaia/repo/{'pull' if contrib_type == 'pull_request' else 'issues'}/{random.randint(100, 999)}"
            
            contributions.append({
                "contributor_username": username,
                "date": contrib_date,
                "type": contrib_type,
                "title": title,
                "description": description,
                "url": url,
                "status": status
            })
    
    # Sort by date
    contributions.sort(key=lambda x: x["date"], reverse=True)
    
    return contributions

def generate_project_metrics():
    """Generate project metrics over time"""
    metrics = []
    
    # Start date (6 months ago)
    start_date = datetime.now() - timedelta(days=180)
    
    # Create metrics for each day
    current_date = start_date
    end_date = datetime.now()
    
    total_contributors = 10  # Start with 10
    
    while current_date <= end_date:
        # Calculate growth rate (more recent = faster growth)
        progress = (current_date - start_date).days / (end_date - start_date).days
        
        # Add daily fluctuations
        daily_new = 0
        if random.random() < (0.1 + 0.3 * progress):  # More likely to add contributors recently
            daily_new = random.choices([0, 1, 2], weights=[0.4, 0.5, 0.1])[0]
        
        total_contributors += daily_new
        
        # Calculate active contributors (60-90% of total)
        active_contributors = int(total_contributors * random.uniform(0.6, 0.9))
        
        # Issues and PRs scale with contributor count
        base_issues = int(total_contributors * 0.8)
        base_prs = int(total_contributors * 0.6)
        
        # Add randomness
        open_issues = max(0, int(base_issues * random.uniform(0.3, 0.5)))
        closed_issues = max(0, int(base_issues * random.uniform(0.5, 0.7)))
        open_prs = max(0, int(base_prs * random.uniform(0.2, 0.4)))
        merged_prs = max(0, int(base_prs * random.uniform(0.6, 0.8)))
        
        # Project popularity metrics
        stars = int(10 + (total_contributors * 3 * progress))
        forks = int(stars * random.uniform(0.2, 0.4))
        
        metrics.append({
            "date": current_date.date(),
            "total_contributors": total_contributors,
            "active_contributors": active_contributors,
            "open_issues": open_issues,
            "closed_issues": closed_issues,
            "open_prs": open_prs,
            "merged_prs": merged_prs,
            "stars": stars,
            "forks": forks
        })
        
        current_date += timedelta(days=1)
    
    return metrics

def populate_database():
    """Populate database with sample data"""
    # Initialize the database schema
    init_db()
    
    # Get database engine
    engine = get_engine()
    if not engine:
        print("Error: Could not connect to database")
        return False
    
    try:
        # Generate data
        print("Generating sample data...")
        contributors = generate_contributor_data(25)
        contributions = generate_contribution_data(contributors)
        metrics = generate_project_metrics()
        
        # Insert contributors
        print(f"Inserting {len(contributors)} contributors...")
        for contributor in contributors:
            query = text("""
            INSERT INTO contributors 
                (username, first_contribution_date, contribution_count, is_active, contribution_type, email, display_name)
            VALUES 
                (:username, :first_contribution_date, :contribution_count, :is_active, :contribution_type, :email, :display_name)
            ON CONFLICT (username) 
            DO UPDATE SET 
                contribution_count = :contribution_count,
                is_active = :is_active
            """)
            
            with engine.connect() as conn:
                conn.execute(query, contributor)
                conn.commit()
        
        # Insert contributions
        print(f"Inserting {len(contributions)} contributions...")
        for contribution in contributions:
            # First get the contributor_id
            username = contribution["contributor_username"]
            get_id_query = text("SELECT id FROM contributors WHERE username = :username")
            
            with engine.connect() as conn:
                result = conn.execute(get_id_query, {"username": username})
                contributor_row = result.fetchone()
                
                if not contributor_row:
                    print(f"Warning: Contributor {username} not found, skipping contribution")
                    continue
                
                contributor_id = contributor_row[0]
                
                # Insert contribution
                query = text("""
                INSERT INTO contributions 
                    (contributor_id, date, type, title, description, url, status)
                VALUES 
                    (:contributor_id, :date, :type, :title, :description, :url, :status)
                """)
                
                conn.execute(
                    query, 
                    {
                        "contributor_id": contributor_id,
                        "date": contribution["date"],
                        "type": contribution["type"],
                        "title": contribution["title"],
                        "description": contribution["description"],
                        "url": contribution["url"],
                        "status": contribution["status"]
                    }
                )
                conn.commit()
        
        # Insert project metrics
        print(f"Inserting {len(metrics)} daily metrics records...")
        for metric in metrics:
            query = text("""
            INSERT INTO project_metrics 
                (date, total_contributors, active_contributors, open_issues, closed_issues, open_prs, merged_prs, stars, forks)
            VALUES 
                (:date, :total_contributors, :active_contributors, :open_issues, :closed_issues, :open_prs, :merged_prs, :stars, :forks)
            ON CONFLICT (date) 
            DO UPDATE SET 
                total_contributors = :total_contributors,
                active_contributors = :active_contributors,
                open_issues = :open_issues,
                closed_issues = :closed_issues,
                open_prs = :open_prs,
                merged_prs = :merged_prs,
                stars = :stars,
                forks = :forks
            """)
            
            with engine.connect() as conn:
                conn.execute(query, metric)
                conn.commit()
        
        # Insert project settings
        print("Inserting project settings...")
        project_settings = [
            {"key": "project_name", "value": "Open Source Project"},
            {"key": "project_description", "value": "An amazing open source project"},
            {"key": "project_repo", "value": "https://github.com/organization/repo"},
            {"key": "current_contributors", "value": "10"},
            {"key": "target_contributors", "value": "50"}
        ]
        
        for setting in project_settings:
            query = text("""
            INSERT INTO project_settings
                (key, value, updated_at)
            VALUES
                (:key, :value, :updated_at)
            ON CONFLICT (key)
            DO UPDATE SET
                value = :value,
                updated_at = :updated_at
            """)
            
            with engine.connect() as conn:
                conn.execute(query, {
                    "key": setting["key"],
                    "value": setting["value"],
                    "updated_at": datetime.now().date()
                })
                conn.commit()
        
        print("Database populated successfully!")
        return True
    
    except Exception as e:
        print(f"Error populating database: {e}")
        return False

if __name__ == "__main__":
    # Execute as standalone script
    populate_database()