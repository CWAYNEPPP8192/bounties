# Open Source Community Dashboard

A comprehensive dashboard and resource hub for growing your open-source community from 10 to 50 contributors. This application provides visualizations, metrics, and resources to help you manage and grow your contributor base.

## Features

- **Community Growth Metrics**: Track progress toward your contributor goals with visual indicators
- **Contributor Journey Visualization**: Map the path from first-time visitor to core maintainer
- **Resource Hub**: Centralized documentation and guides for contributors
- **Project Roadmap**: Visual timeline of project development plans and milestones
- **Metrics Analytics**: Detailed statistics on community growth and engagement
- **Database Admin**: Tools for managing contributor data
- **Configurable Settings**: Customize the dashboard for any open source project

## Setup and Installation

### Prerequisites

- Python 3.8+
- SQLite (included) or PostgreSQL database

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/community-dashboard.git
   cd community-dashboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure database:
   - For SQLite (default): No additional configuration needed
   - For PostgreSQL: Set `DATABASE_URL` environment variable

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Configuration

The dashboard is fully configurable to work with any open source project. Key settings are stored in the database and can be modified through the Project Settings page:

- **Project Name**: The name of your open source project
- **Project Description**: A brief description of your project
- **Current Contributors**: Your starting contributor count
- **Target Contributors**: Your contributor goal

## Database Structure

The application uses a database with the following tables:

- `project_settings`: Stores configurable dashboard elements
- `contributors`: Information about project contributors
- `contributions`: Records of individual contributions
- `project_metrics`: Time-series metrics data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.