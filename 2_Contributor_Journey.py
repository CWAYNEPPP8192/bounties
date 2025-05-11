import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Contributor Journey | Open Source",
    page_icon="🌱",
    layout="wide"
)

import altair as alt
import pandas as pd
import sys
import os

# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database_fixed import get_project_settings

# Get project settings
project_name, project_description, current_contributors, target_contributors = get_project_settings()
project_tagline = "Open Source Community"  # Default value

# Header
st.title("🚶‍♀️ Contributor Journey Visualization")
st.markdown(f"""
This page visualizes the journey from a first-time contributor to a core maintainer in the {project_name} ecosystem.
Understanding this journey helps us identify obstacles and opportunities to expand our contributor base.
""")

# Contributor journey diagram
st.header("Contributor Progression Path")

# Journey stages data
journey_stages = [
    {"stage": 1, "name": "Discovery", "description": "Finding out about Gaia project", "typical_activities": "Reading documentation, exploring website", "avg_duration": "N/A", "conversion": "100%"},
    {"stage": 2, "name": "First Contact", "description": "Initial interaction with community", "typical_activities": "Joining Discord, GitHub star, asking questions", "avg_duration": "1-7 days", "conversion": "40%"},
    {"stage": 3, "name": "First Contribution", "description": "Making initial small contribution", "typical_activities": "Small PR, documentation fix, issue reporting", "avg_duration": "2-3 weeks", "conversion": "20%"},
    {"stage": 4, "name": "Regular Contributor", "description": "Consistent contribution pattern", "typical_activities": "Multiple PRs, issue discussions, helping others", "avg_duration": "1-3 months", "conversion": "8%"},
    {"stage": 5, "name": "Trusted Contributor", "description": "Recognized expertise in specific areas", "typical_activities": "Feature implementation, code reviews, mentoring", "avg_duration": "3-6 months", "conversion": "5%"},
    {"stage": 6, "name": "Maintainer", "description": "Core team member with broad responsibilities", "typical_activities": "Architectural decisions, release management, community leadership", "avg_duration": "6+ months", "conversion": "2%"}
]

# Convert to dataframe for visualization
journey_df = pd.DataFrame(journey_stages)

# Create a horizontal progress bar-like chart
journey_chart = alt.Chart(journey_df).mark_rect().encode(
    x=alt.X('stage:O', title="Journey Stage", axis=alt.Axis(labelAngle=0)),
    color=alt.Color('conversion:N', scale=alt.Scale(scheme='blues'), legend=None),
    tooltip=['name', 'description', 'typical_activities', 'avg_duration', 'conversion']
).properties(
    height=100
)

# Add text labels
text_chart = alt.Chart(journey_df).mark_text(align='center', baseline='middle', dy=-15).encode(
    x=alt.X('stage:O'),
    text='name:N'
)

# Combine the charts
final_chart = journey_chart + text_chart

# Display chart
st.altair_chart(final_chart, use_container_width=True)

# Journey stages details
st.subheader("Journey Stages Explained")

for idx, stage in enumerate(journey_stages):
    with st.expander(f"{idx+1}. {stage['name']} - {stage['description']}"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Typical Activities:**")
            st.markdown(stage['typical_activities'])
            st.markdown(f"**Average Duration:** {stage['avg_duration']}")
        with col2:
            st.markdown("**Conversion Rate:**")
            st.markdown(f"{stage['conversion']} of users progress from previous stage")
            st.markdown("**Key Incentives:**")
            incentives = {
                1: "Interest in the technology, problem-solving curiosity",
                2: "Welcoming community, clear documentation, quick responses",
                3: "Recognition, 'good first issue' tags, clear contribution process",
                4: "Mentorship, skill development, resume building, project ownership",
                5: "Community status, decision-making input, deeper involvement",
                6: "Leadership opportunities, career advancement, project direction influence"
            }
            st.markdown(incentives.get(idx+1, ""))

# Engagement pathways
st.header("Engagement Pathways")
st.markdown(f"""
There are multiple pathways to becoming a valuable contributor to {project_name}. Each person's journey is unique,
but we've identified several common patterns that help us understand how to better support different
types of contributors.
""")

# Pathway tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Technical Contributor", 
    "Community Supporter", 
    "Content Creator",
    "Domain Expert"
])

with tab1:
    st.subheader("Technical Contributor Path")
    st.markdown("""
    The classic path of contributing code and technical improvements to the project.
    
    **Entry Point:**
    - Finding a bug that affects their use case
    - Wanting to add a feature they need
    - Hackathons or coding events
    
    **Progression:**
    1. Fix simple bugs or documentation
    2. Implement small features
    3. Take on more complex technical challenges
    4. Review others' code
    5. Make architectural decisions
    
    **Support Needed:**
    - Clear development setup instructions
    - Well-defined issues with sufficient context
    - Technical mentorship
    - Code review feedback
    """)
    
    st.info("**Success Story:** Developer Jane started by fixing a documentation typo, then addressed a minor bug, and is now leading the authentication module refactoring after 4 months of involvement.")

with tab2:
    st.subheader("Community Supporter Path")
    st.markdown("""
    Focuses on helping other users, improving documentation, and building community.
    
    **Entry Point:**
    - Answering questions on forums/Discord
    - Helping new users get started
    - Organizing community events
    
    **Progression:**
    1. Answering basic questions in community channels
    2. Creating helpful resources and guides
    3. Improving official documentation
    4. Mentoring new contributors
    5. Community management and leadership
    
    **Support Needed:**
    - Recognition for non-code contributions
    - Clear community guidelines
    - Communication channels for coordination
    - Templates and resources to assist others
    """)
    
    st.info("**Success Story:** Community member Alex started by answering questions in Discord, created several guides to help newcomers, and now coordinates our mentorship program and onboarding process.")

with tab3:
    st.subheader("Content Creator Path")
    st.markdown(f"""
    Creates tutorials, blog posts, videos and other educational content about {project_name}.
    
    **Entry Point:**
    - Writing about their experience using {project_name}
    - Creating a tutorial to remember how they solved a problem
    - Sharing knowledge with their network
    
    **Progression:**
    1. Creating basic usage tutorials
    2. Writing blog posts about specific features
    3. Making comprehensive video guides
    4. Presenting at conferences or webinars
    5. Developing official learning resources
    
    **Support Needed:**
    - Access to project roadmap and updates
    - Brand assets and guidelines
    - Promotion of their content
    - Early access to new features
    """)
    
    st.info(f"**Success Story:** YouTuber Sam created a 'Getting Started with {project_name}' video series that brought in hundreds of new users, and now collaborates with the core team on official tutorial content.")

with tab4:
    st.subheader("Domain Expert Path")
    st.markdown(f"""
    Brings specialized knowledge in the problem domain that {project_name} addresses.
    
    **Entry Point:**
    - Professional expertise related to {project_name}'s purpose
    - Academic or research background in relevant field
    - Practical experience with similar systems
    
    **Progression:**
    1. Providing domain-specific feedback
    2. Suggesting features based on field expertise
    3. Helping validate solutions against real-world needs
    4. Guiding strategic direction in their domain
    5. Representing project to industry stakeholders
    
    **Support Needed:**
    - Avenues to provide specialized input
    - Connection to technical contributors
    - Recognition of domain expertise
    - Involvement in strategic discussions
    """)
    
    st.info("**Success Story:** Environmental scientist Dr. Chen provided crucial input on data models for ecosystem analysis, improving accuracy and adoption among research institutions.")

# Contributor Support Framework
st.header("Contributor Support Framework")

# Two columns for the framework
col1, col2 = st.columns(2)

with col1:
    st.subheader("Contributor Onboarding")
    st.markdown("""
    We've designed a systematic approach to welcome and support new contributors:
    
    1. **Welcome Pack**
       - Personalized greeting in Discord
       - First-time contributor guide
       - Development environment setup scripts
    
    2. **Guided First Contribution**
       - Curated "good first issues"
       - Step-by-step PR creation walkthrough
       - Guaranteed review within 48 hours
    
    3. **Early Recognition**
       - Acknowledgment in release notes
       - Contributor spotlight for first PR
       - Digital badge for GitHub profile
    """)
    
    st.subheader("Retention Strategies")
    st.markdown("""
    Keeping contributors engaged over time:
    
    1. **Skill Development**
       - Targeted technical challenges
       - Learning resources for project technologies
       - Cross-functional collaboration opportunities
    
    2. **Community Connection**
       - Regular 1:1 check-ins with maintainers
       - Virtual coffee breaks and social events
       - Regional meetups where possible
    
    3. **Progressive Responsibility**
       - Graduated access to repository permissions
       - Mentoring newer contributors
       - Ownership of specific components or features
    """)

with col2:
    st.subheader("Barriers to Contribution")
    st.markdown("""
    We've identified common obstacles and our solutions:
    
    | Barrier | Solution |
    |---------|----------|
    | Complex setup process | One-command development environment |
    | Unclear where to start | Tagged issues by experience level |
    | Long feedback cycles | 48-hour review guarantee |
    | Feeling intimidated | Beginner-friendly communication guidelines |
    | Time constraints | Good first issues requiring <2 hours |
    | Imposter syndrome | Explicit encouragement and mentorship |
    """)
    
    st.subheader("Success Metrics")
    st.markdown("""
    How we measure the effectiveness of our contributor journey:
    
    **Conversion Metrics:**
    - % of GitHub stargazers who make first contribution
    - % of first-time contributors who make second contribution
    - % of regular contributors who become trusted contributors
    
    **Time-based Metrics:**
    - Average time from first interaction to first contribution
    - Average time between contributions
    - Contributor retention at 3/6/12 months
    
    **Diversity Metrics:**
    - Geographic distribution of contributors
    - Range of contribution types (code, docs, community)
    - New vs. experienced open source contributors
    """)

# Tools and resources
st.header("Tools & Resources for Contributors")

tool_col1, tool_col2, tool_col3 = st.columns(3)

with tool_col1:
    st.subheader("Technical Resources")
    st.markdown("""
    - **Development VM**: Pre-configured development environment
    - **Local Testing Suite**: Automated test environment
    - **VS Code Extensions**: Project-specific extensions for productivity
    - **CI/CD Pipeline Documentation**: Understanding our build processes
    """)

with tool_col2:
    st.subheader("Community Resources")
    st.markdown("""
    - **Discord Channels**: Organized by topic and expertise level
    - **Office Hours**: Weekly video calls with maintainers
    - **Pair Programming Sessions**: Scheduled coding help sessions
    - **Mentorship Matching**: Connect with experienced contributors
    """)

with tool_col3:
    st.subheader("Learning Resources")
    st.markdown("""
    - **Contribution Cookbook**: Step-by-step guides for common tasks
    - **Architecture Documentation**: System design and patterns
    - **Video Tutorials**: Recorded walkthroughs of contribution process
    - **Code Reading Club**: Group sessions to understand codebase areas
    """)

# Call to action
st.success(f"""
**Where are you in your contributor journey?**

Whether you're just discovering {project_name} or are already an active contributor, we have resources to support your next steps.
Visit our [Community Resources](Community_Resources) page to find the right entry point for your journey.
""")

# footer
st.markdown("---")
st.caption(f"{project_name} Open Source Community Dashboard - Helping grow our community from {current_contributors} to {target_contributors} active contributors")
