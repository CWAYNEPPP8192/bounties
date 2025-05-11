import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from sqlalchemy import text
import sys
import os

# Import database functions
sys.path.append(os.path.join(os.getcwd(), 'utils'))
from utils.database_fixed import get_engine

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
    page_title=f"Project Roadmap | {project_name}",
    page_icon="🗺️",
    layout="wide"
)

# Header
st.title("🗺️ Project Roadmap & Open Issues")
st.markdown(f"""
Explore {project_name}'s development roadmap and find open issues that match your interests and skills.
This page helps you understand where the project is headed and how you can contribute to its success.
""")

# Define current date for the roadmap timeline
today = datetime.now()

# Create sample roadmap data (this would come from GitHub/project management tools in a real app)
roadmap_data = [
    {
        "milestone": "Community Growth Foundation",
        "description": "Establish core infrastructure for community growth",
        "start_date": today - timedelta(days=30),
        "end_date": today + timedelta(days=30),
        "status": "In Progress",
        "completion": 60,
        "key_deliverables": [
            "Contributor onboarding documentation",
            "Automated development environment",
            "Community metrics dashboard"
        ]
    },
    {
        "milestone": "Feature X Development",
        "description": "Implement highly requested user feature",
        "start_date": today + timedelta(days=15),
        "end_date": today + timedelta(days=75),
        "status": "Planning",
        "completion": 10,
        "key_deliverables": [
            "Technical specification",
            "Core implementation",
            "Integration with existing systems",
            "User documentation"
        ]
    },
    {
        "milestone": "Performance Optimization",
        "description": "Improve system performance and reduce resource usage",
        "start_date": today + timedelta(days=60),
        "end_date": today + timedelta(days=120),
        "status": "Not Started",
        "completion": 0,
        "key_deliverables": [
            "Performance audit",
            "Database query optimization",
            "Frontend rendering improvements",
            "Caching strategy implementation"
        ]
    },
    {
        "milestone": "v2.0 Release",
        "description": "Major version release with breaking changes",
        "start_date": today + timedelta(days=150),
        "end_date": today + timedelta(days=180),
        "status": "Not Started",
        "completion": 0,
        "key_deliverables": [
            "Feature freeze and stability testing",
            "Migration guides and tools",
            "Updated documentation",
            "Community announcement and webinar"
        ]
    }
]

# Convert to DataFrame for easier handling
roadmap_df = pd.DataFrame(roadmap_data)

# Main content - split into tabs
tab1, tab2, tab3 = st.tabs(["Roadmap Timeline", "Open Issues", "Contributing Opportunities"])

with tab1:
    st.header("Project Roadmap Timeline")
    st.markdown(f"""
    Below is {project_name}'s development roadmap for the coming months. This timeline shows major milestones,
    their status, and expected delivery dates. The roadmap is regularly updated based on community
    feedback and project priorities.
    """)
    
    # Create visual timeline using Altair
    # Process data for visualization
    timeline_data = []
    for idx, milestone in enumerate(roadmap_data):
        timeline_data.append({
            "milestone": milestone["milestone"],
            "start": milestone["start_date"].strftime("%Y-%m-%d"),
            "end": milestone["end_date"].strftime("%Y-%m-%d"),
            "completion": milestone["completion"],
            "status": milestone["status"],
            "index": idx
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    
    # Create chart
    timeline_chart = alt.Chart(timeline_df).mark_bar().encode(
        x='start:T',
        x2='end:T',
        y=alt.Y('milestone:N', sort=None),
        color=alt.Color('status:N', scale=alt.Scale(domain=['Not Started', 'Planning', 'In Progress', 'Completed'],
                                                 range=['#d3d3d3', '#ffcc00', '#33cc33', '#3366ff'])),
        tooltip=['milestone', 'status', 'start', 'end', 'completion']
    ).properties(
        height=200
    )
    
    # Add today marker
    today_df = pd.DataFrame([{'date': today.strftime("%Y-%m-%d")}])
    today_rule = alt.Chart(today_df).mark_rule(color='red').encode(
        x='date:T'
    )
    
    # Combine charts
    final_chart = timeline_chart + today_rule
    
    # Display chart
    st.altair_chart(final_chart, use_container_width=True)
    
    # Display milestone details
    st.subheader("Milestone Details")
    
    for milestone in roadmap_data:
        with st.expander(f"{milestone['milestone']} - {milestone['status']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description:** {milestone['description']}")
                st.markdown("**Key Deliverables:**")
                for deliverable in milestone["key_deliverables"]:
                    st.markdown(f"- {deliverable}")
            
            with col2:
                st.markdown(f"**Timeline:** {milestone['start_date'].strftime('%b %d')} - {milestone['end_date'].strftime('%b %d, %Y')}")
                st.markdown(f"**Completion:** {milestone['completion']}%")
                st.progress(milestone['completion']/100)
                
                # Show appropriate call to action based on status
                if milestone['status'] == "Not Started":
                    st.info("Opportunity to contribute to early planning")
                elif milestone['status'] == "Planning":
                    st.info("Looking for input on requirements and design")
                elif milestone['status'] == "In Progress":
                    st.info("Active development - contributors needed")
                else:
                    st.success("Completed - feedback welcome")

with tab2:
    st.header("Open Issues")
    st.markdown(f"""
    Browse current open issues in the {project_name} project. You can filter by category, difficulty level,
    and status to find issues that match your interests and expertise.
    """)
    
    # Create columns for filters
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        category_filter = st.multiselect(
            "Category",
            ["Bug", "Feature", "Documentation", "Performance", "Security", "UI/UX"],
            default=["Bug", "Feature", "Documentation"]
        )
    
    with filter_col2:
        difficulty_filter = st.multiselect(
            "Difficulty",
            ["Good First Issue", "Easy", "Medium", "Hard"],
            default=["Good First Issue", "Easy"]
        )
    
    with filter_col3:
        status_filter = st.multiselect(
            "Status",
            ["Open", "In Progress", "Ready for Review"],
            default=["Open"]
        )
    
    # Sample issue data (would come from GitHub API in a real implementation)
    issues_data = [
        {
            "id": 1001,
            "title": "Fix typo in API documentation",
            "description": "There's a typo in the authentication section of the API docs.",
            "category": "Documentation",
            "difficulty": "Good First Issue",
            "status": "Open",
            "created_at": "2023-06-15",
            "assigned_to": None,
            "url": "https://github.com/gaia/repo/issues/1001"
        },
        {
            "id": 1002,
            "title": "Improve error messages in user registration flow",
            "description": "Current error messages are too technical. Need more user-friendly messages.",
            "category": "UI/UX",
            "difficulty": "Easy",
            "status": "Open",
            "created_at": "2023-06-20",
            "assigned_to": None,
            "url": "https://github.com/gaia/repo/issues/1002"
        },
        {
            "id": 1003,
            "title": "Add pagination to search results",
            "description": "Search results should be paginated to improve performance with large result sets.",
            "category": "Feature",
            "difficulty": "Medium",
            "status": "In Progress",
            "created_at": "2023-06-10",
            "assigned_to": "contributor1",
            "url": "https://github.com/gaia/repo/issues/1003"
        },
        {
            "id": 1004,
            "title": "Optimize database queries for dashboard",
            "description": "Dashboard loading is slow due to inefficient queries. Need optimization.",
            "category": "Performance",
            "difficulty": "Hard",
            "status": "Open",
            "created_at": "2023-06-05",
            "assigned_to": None,
            "url": "https://github.com/gaia/repo/issues/1004"
        },
        {
            "id": 1005,
            "title": "Fix CORS issue with API endpoints",
            "description": "API endpoints are not properly handling CORS headers for cross-origin requests.",
            "category": "Bug",
            "difficulty": "Medium",
            "status": "Ready for Review",
            "created_at": "2023-06-18",
            "assigned_to": "contributor2",
            "url": "https://github.com/gaia/repo/issues/1005"
        },
        {
            "id": 1006,
            "title": "Add unit tests for auth module",
            "description": "The authentication module needs additional test coverage.",
            "category": "Feature",
            "difficulty": "Medium",
            "status": "Open",
            "created_at": "2023-06-22",
            "assigned_to": None,
            "url": "https://github.com/gaia/repo/issues/1006"
        },
        {
            "id": 1007,
            "title": "Update contributor guidelines",
            "description": "Contributor guidelines need updating to include new development workflow.",
            "category": "Documentation",
            "difficulty": "Easy",
            "status": "Open",
            "created_at": "2023-06-25",
            "assigned_to": None,
            "url": "https://github.com/gaia/repo/issues/1007"
        },
        {
            "id": 1008,
            "title": "Fix security vulnerability in file upload",
            "description": "File upload feature has potential security issues with certain file types.",
            "category": "Security",
            "difficulty": "Hard",
            "status": "In Progress",
            "created_at": "2023-06-12",
            "assigned_to": "maintainer1",
            "url": "https://github.com/gaia/repo/issues/1008"
        }
    ]
    
    # Filter issues based on selections
    filtered_issues = [
        issue for issue in issues_data
        if issue["category"] in category_filter
        and issue["difficulty"] in difficulty_filter
        and issue["status"] in status_filter
    ]
    
    # Display number of results
    st.write(f"Showing {len(filtered_issues)} of {len(issues_data)} issues")
    
    # Display issues in expandable format
    if not filtered_issues:
        st.info("No issues match your current filters. Try adjusting your criteria.")
    else:
        for issue in filtered_issues:
            with st.expander(f"#{issue['id']}: {issue['title']} [{issue['difficulty']}]"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:** {issue['description']}")
                    st.markdown(f"**Category:** {issue['category']}")
                    if issue['assigned_to']:
                        st.markdown(f"**Assigned to:** @{issue['assigned_to']}")
                    else:
                        st.markdown("**Assigned to:** _Unassigned_")
                
                with col2:
                    st.markdown(f"**Status:** {issue['status']}")
                    st.markdown(f"**Created:** {issue['created_at']}")
                    
                    # Add action button
                    if issue['status'] == 'Open' and not issue['assigned_to']:
                        st.button(f"Express Interest #{issue['id']}", key=f"interest_{issue['id']}")
                    
                    # Link to GitHub
                    st.markdown(f"[View on GitHub]({issue['url']})")

with tab3:
    st.header("Contributing Opportunities")
    st.markdown(f"""
    Beyond addressing specific issues, there are many ways to contribute to the {project_name} project.
    Below are some ongoing initiatives and areas where we welcome community involvement.
    """)
    
    # Create columns for different contribution types
    cont_col1, cont_col2 = st.columns(2)
    
    with cont_col1:
        st.subheader("Code Contributions")
        
        with st.expander("🧪 Testing and Quality Assurance"):
            st.markdown(f"""
            Help improve {project_name}'s stability and reliability through testing:
            
            - Write unit tests for existing functionality
            - Perform manual testing of new features
            - Set up automated testing infrastructure
            - Create integration tests for critical workflows
            
            **Skills Needed:** Testing frameworks, attention to detail, software quality best practices
            
            **Getting Started:** Review our [testing guide](https://docs.gaia.org/testing) and check issues labeled with `testing` or `qa`
            """)
        
        with st.expander("🏎️ Performance Optimization"):
            st.markdown(f"""
            Help make {project_name} faster and more efficient:
            
            - Identify performance bottlenecks
            - Optimize slow database queries
            - Improve frontend rendering performance
            - Implement caching strategies
            
            **Skills Needed:** Profiling tools, database optimization, algorithm analysis
            
            **Getting Started:** Check issues labeled with `performance` or join our #performance channel on Discord
            """)
        
        with st.expander("🧰 Developer Tools"):
            st.markdown(f"""
            Improve the developer experience for all {project_name} contributors:
            
            - Create developer utilities and scripts
            - Improve build and deployment processes
            - Enhance local development environment
            - Create VS Code extensions or editor plugins
            
            **Skills Needed:** DevOps, scripting, development workflows
            
            **Getting Started:** Join the #dev-tools channel on Discord to discuss current needs
            """)
        
        with st.expander("🔍 Code Review"):
            st.markdown("""
            Help maintain code quality through thoughtful reviews:
            
            - Review open pull requests
            - Provide constructive feedback
            - Verify bug fixes and implementations
            - Ensure adherence to project standards
            
            **Skills Needed:** Attention to detail, communication skills, technical expertise
            
            **Getting Started:** Browse open PRs and add comments, or ask a maintainer to be added as a reviewer
            """)
    
    with cont_col2:
        st.subheader("Non-Code Contributions")
        
        with st.expander("📚 Documentation"):
            st.markdown(f"""
            Improve {project_name}'s documentation for users and contributors:
            
            - Update existing documentation
            - Create tutorials and guides
            - Translate documentation to other languages
            - Create diagrams and visualizations
            
            **Skills Needed:** Clear writing, technical communication, attention to detail
            
            **Getting Started:** Check issues labeled with `documentation` or suggest improvements directly
            """)
        
        with st.expander("👨‍🏫 Community Support"):
            st.markdown(f"""
            Help other users and contributors succeed with {project_name}:
            
            - Answer questions in Discord and forums
            - Create helpful resources for common issues
            - Mentor new contributors
            - Facilitate community events
            
            **Skills Needed:** Patience, communication skills, technical knowledge
            
            **Getting Started:** Join our community channels and start helping others
            """)
        
        with st.expander("🎨 Design and UX"):
            st.markdown(f"""
            Improve the user experience and visual design of {project_name}:
            
            - Create UI mockups for new features
            - Conduct usability testing
            - Improve accessibility
            - Design visual assets and iconography
            
            **Skills Needed:** UI/UX design, visual design, accessibility knowledge
            
            **Getting Started:** Join the #design channel on Discord or check issues labeled with `design` or `ux`
            """)
        
        with st.expander("📢 Advocacy and Outreach"):
            st.markdown(f"""
            Help spread the word about {project_name} and grow our community:
            
            - Write blog posts about {project_name}
            - Create tutorial videos
            - Speak at events and conferences
            - Engage with the broader tech community
            
            **Skills Needed:** Communication, content creation, networking
            
            **Getting Started:** Join our #advocacy channel or contact the community team with your ideas
            """)
    
    # Special initiatives section
    st.subheader("Special Initiatives and Working Groups")
    st.markdown("""
    Join one of our focused initiatives to make a significant impact in a specific area:
    """)
    
    initiative_col1, initiative_col2, initiative_col3 = st.columns(3)
    
    with initiative_col1:
        st.markdown("""
        ### 🌟 Onboarding Initiative
        
        Improving the experience for new users and contributors.
        
        **Current Focus:** Creating interactive tutorials.
        
        **Meeting:** Tuesdays at 18:00 UTC
        
        [Learn More](#)
        """)
    
    with initiative_col2:
        st.markdown(f"""
        ### 🌐 Internationalization Group
        
        Making {project_name} accessible in multiple languages.
        
        **Current Focus:** Translation infrastructure and docs.
        
        **Meeting:** Thursdays at 16:00 UTC
        
        [Learn More](#)
        """)
    
    with initiative_col3:
        st.markdown("""
        ### ⚡ Performance Task Force
        
        Systematic approach to performance improvements.
        
        **Current Focus:** Database optimization.
        
        **Meeting:** Wednesdays at 20:00 UTC
        
        [Learn More](#)
        """)

# Add contributor spotlights and success stories
st.header("Contributor Spotlights")
st.markdown(f"""
Learn from the experiences of some of our valued contributors and how they've grown within the {project_name} community.
""")

spotlight_col1, spotlight_col2 = st.columns(2)

with spotlight_col1:
    st.markdown(f"""
    ### Maria T. - From First PR to Core Maintainer
    
    > "I started with a simple documentation fix and within 6 months found myself helping design major features. The {project_name} community welcomed me and provided mentorship every step of the way."
    
    **Contribution Journey:**
    - First contribution: Fixing API documentation
    - Notable work: Redesigned the user authentication system
    - Current role: Core maintainer and security team lead
    - Time with project: 1.5 years
    """)

with spotlight_col2:
    st.markdown(f"""
    ### Raj S. - Non-Coding Contributor
    
    > "As someone without a strong coding background, I wasn't sure how I could help. But my experience in technical writing allowed me to completely revamp the documentation, making {project_name} more accessible to new users."
    
    **Contribution Journey:**
    - First contribution: Improving installation instructions
    - Notable work: Created the comprehensive contributor's guide
    - Current role: Documentation team lead
    - Time with project: 8 months
    """)

# Call to action
st.success(f"""
**Ready to contribute to {project_name}'s roadmap?**

1. Check the [Open Issues](#open-issues) tab to find something that matches your skills
2. Join our [Discord community](https://discord.gg/{project_name.lower()}) to connect with other contributors
3. Attend our next community call (every other Thursday) to learn more about current priorities

Your contributions, big or small, help drive {project_name} forward!
""")

# footer
st.markdown("---")
st.caption("Gaia Open Source Community Dashboard - Helping grow our community from 10 to 50 active contributors")
