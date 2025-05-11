# Contributing to the Open Source Community Dashboard

Thank you for your interest in contributing to the Open Source Community Dashboard! This document outlines the process for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

- **Use the GitHub issue tracker** to report bugs
- **Describe the bug in detail** - include steps to reproduce, expected behavior, and actual behavior
- **Include screenshots** if applicable
- **Note your environment** - OS, browser, Python version, etc.

### Suggesting Enhancements

- **Use the GitHub issue tracker** to suggest enhancements
- **Provide a clear description** of the feature and its benefits
- **Include mockups or examples** if possible

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install development dependencies** by following the setup instructions in the README
3. **Make your changes** following the coding style of the project
4. **Add tests** for any new functionality
5. **Ensure all tests pass** by running the test suite
6. **Update documentation** to reflect any changes
7. **Submit your pull request** with a clear description of the changes

## Development Process

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/community-dashboard.git
cd community-dashboard

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Project Structure

- `app.py` - Main application entry point
- `pages/` - Dashboard pages
- `utils/` - Helper modules and database tools
- `data/` - Sample data generators

### Coding Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Include docstrings for functions and classes
- Keep functions small and focused on a single task

## Database Management

When making changes that require database schema updates:

1. Document the changes in your pull request
2. Update the database schema initialization in `utils/database_fixed.py`
3. Provide migration instructions if needed

Thank you for contributing!