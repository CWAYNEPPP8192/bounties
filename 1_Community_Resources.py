import streamlit as st
import pandas as pd
from utils.database_fixed import get_engine

# Page configuration
st.set_page_config(
    page_title="Community Resources | Open Source Dashboard",
    page_icon="🌱",
    layout="wide"
)

# Get project info from database
engine = get_engine()
project_name = "Open Source Project"
project_description = "An amazing open source project"
project_repo = "https://github.com/organization/repo"

if engine:
    try:
        # Try to get project info from database
        query = "SELECT value FROM project_settings WHERE key = 'project_name';"
        df = pd.read_sql(query, engine)
        if not df.empty:
            project_name = df.iloc[0]['value']
            
        query = "SELECT value FROM project_settings WHERE key = 'project_description';"
        df = pd.read_sql(query, engine)
        if not df.empty:
            project_description = df.iloc[0]['value']
            
        query = "SELECT value FROM project_settings WHERE key = 'project_repo';"
        df = pd.read_sql(query, engine)
        if not df.empty:
            project_repo = df.iloc[0]['value']
    except Exception as e:
        st.warning(f"Could not load project settings: {e}")

# Header
st.title(f"🔍 {project_name} Community Resources")
st.markdown(f"""
This page provides all the resources you need to become an effective contributor
to the {project_name} project. Whether you're looking to make your first contribution
or are a seasoned community member, you'll find valuable information here.
""")

# Main content - split into tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Getting Started", 
    "Contribution Process", 
    "Code Standards", 
    "Community Guidelines"
])

with tab1:
    st.header(f"Getting Started with {project_name}")
    
    st.subheader(f"What is {project_name}?")
    st.markdown(f"""
    {project_name} is an open-source project focused on {project_description}. 
    Our mission is to grow a vibrant and inclusive open source community.
    We welcome contributors of all skill levels and backgrounds.
    """)
    
    st.subheader("Prerequisites")
    st.markdown("""
    Before you begin, make sure you have:
    
    - A GitHub account
    - Git installed locally
    - Basic understanding of [relevant technologies]
    - Familiarity with pull request workflows
    """)
    
    st.subheader("First Steps")
    st.markdown(f"""
    1. **Star and Fork the Repository**: Visit the [{project_name} GitHub repository]({project_repo})
    2. **Set Up Your Development Environment**: Follow our setup guide in the repository README
    3. **Find a Good First Issue**: Look for issues tagged with `good-first-issue` or `beginner-friendly`
    4. **Join Our Community Channels**: See the Community section below
    """)

with tab2:
    st.header("Contribution Process")
    
    st.subheader("Step-by-Step Guide")
    st.markdown("""
    1. **Find an Issue**: Browse open issues or propose a new one
    2. **Claim the Issue**: Comment on the issue to express your interest
    3. **Fork and Clone**: Set up your local development environment
    4. **Create a Branch**: Use a descriptive name like `feature/add-login` or `fix/header-display`
    5. **Make Changes**: Implement your feature or fix with appropriate tests
    6. **Commit Changes**: Follow our commit message guidelines
    7. **Submit a Pull Request**: Include a clear description and reference the issue
    8. **Code Review**: Address feedback from maintainers
    9. **Merge**: Once approved, a maintainer will merge your contribution
    """)
    
    st.subheader("Pull Request Guidelines")
    st.markdown("""
    When submitting a pull request:
    
    - Provide a clear, descriptive title
    - Reference the issue number(s) being addressed
    - Include a summary of changes made
    - Add screenshots for UI changes
    - Make sure all tests pass
    - Request review from relevant team members
    """)

with tab3:
    st.header("Code Standards & Best Practices")
    
    st.subheader("Code Style")
    st.markdown("""
    - We follow [specific style guide] for our codebase
    - Use consistent indentation (spaces, not tabs)
    - Maximum line length of 100 characters
    - Include meaningful comments for complex logic
    - Write self-documenting code with clear variable names
    """)
    
    st.subheader("Testing Requirements")
    st.markdown("""
    - All new features should include tests
    - Maintain or improve code coverage
    - Tests should be meaningful and test actual functionality
    - Both unit and integration tests are valued
    """)
    
    st.subheader("Documentation")
    st.markdown("""
    - Update relevant documentation for any feature changes
    - Add JSDoc/docstring comments for functions
    - Update the README.md if necessary
    - Consider adding examples for API changes
    """)

with tab4:
    st.header("Community Guidelines & Communication")
    
    st.subheader("Code of Conduct")
    st.markdown("""
    We are committed to providing a welcoming and inclusive environment for all contributors.
    Please read our [full Code of Conduct](https://github.com/gaia/code-of-conduct) before participating.
    
    Key principles:
    - Be respectful and inclusive
    - Exercise empathy and kindness
    - Provide and accept constructive feedback
    - Focus on what's best for the community
    """)
    
    st.subheader("Communication Channels")
    st.markdown("""
    - **GitHub Issues**: Technical discussions and bug reports
    - **Discord Server**: Real-time chat and community support
    - **Community Calls**: Bi-weekly on Thursdays (see calendar)
    - **Mailing List**: Major announcements and discussions
    """)
    
    st.subheader("Mentorship Program")
    st.markdown("""
    We offer mentorship for new contributors! If you're interested in being paired with
    an experienced contributor who can guide you through your first contributions, please
    fill out our [mentorship form](https://forms.gaia.org/mentorship).
    """)

# Resource links section
st.header("Essential Resources")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Documentation")
    st.markdown("""
    - [Official Documentation](https://docs.gaia.org)
    - [API Reference](https://docs.gaia.org/api)
    - [Architecture Overview](https://docs.gaia.org/architecture)
    - [Tutorials](https://docs.gaia.org/tutorials)
    """)
    
    st.subheader("Development")
    st.markdown("""
    - [Development Setup Guide](https://docs.gaia.org/dev-setup)
    - [Local Testing Guide](https://docs.gaia.org/testing)
    - [Debugging Tips](https://docs.gaia.org/debugging)
    - [Performance Best Practices](https://docs.gaia.org/performance)
    """)

with col2:
    st.subheader("Community")
    st.markdown("""
    - [GitHub Repository](https://github.com/gaia/repo)
    - [Discord Server](https://discord.gg/gaia)
    - [Community Forum](https://forum.gaia.org)
    - [Events Calendar](https://gaia.org/events)
    """)
    
    st.subheader("First-time Contributors")
    st.markdown("""
    - [Good First Issues](https://github.com/gaia/repo/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22)
    - [Beginner's Guide](https://docs.gaia.org/beginners)
    - [FAQ for New Contributors](https://docs.gaia.org/faq)
    - [Contribution Examples](https://docs.gaia.org/examples)
    """)

# FAQ Accordion
st.header("Frequently Asked Questions")

with st.expander("How long does it take for my PR to be reviewed?"):
    st.markdown("""
    We aim to provide initial feedback on pull requests within 3 business days. More complex changes may take longer to review thoroughly. If you haven't received feedback after a week, feel free to comment on the PR asking for a status update.
    """)

with st.expander("Can I contribute if I'm not a developer?"):
    st.markdown("""
    Absolutely! We welcome contributions in many forms including:
    
    - Documentation improvements
    - Design assets
    - User testing
    - Translation
    - Bug reports
    - Feature suggestions
    
    Check out our [non-code contributions guide](https://docs.gaia.org/non-code-contributions) for more information.
    """)

with st.expander("How do I get help if I'm stuck?"):
    st.markdown("""
    If you're stuck, there are several ways to get help:
    
    1. Comment on the GitHub issue you're working on
    2. Ask in the #help-needed channel on Discord
    3. Join our weekly office hours on Tuesdays
    4. Check if there's similar issues that have been resolved in the past
    
    Remember, everyone was a beginner once - we're happy to help!
    """)

with st.expander("How can I suggest a new feature?"):
    st.markdown("""
    We welcome feature suggestions! To propose a new feature:
    
    1. Check existing issues to make sure it hasn't been suggested
    2. Create a new issue with the "feature request" template
    3. Provide as much detail as possible about the feature and its use cases
    4. Be prepared to discuss and refine the idea with the community
    
    Significant features may require a formal proposal document.
    """)

# Call to action
st.success("""
**Ready to make your first contribution?** 
Start by exploring our [good first issues](https://github.com/gaia/repo/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) 
or join our Discord community to introduce yourself!
""")

# footer
st.markdown("---")
st.caption(f"{project_name} Community Dashboard - Helping grow our community from 10 to 50 active contributors")
