# Book App - Digital Library Platform

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-v13+-blue.svg)
![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)
![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)

A comprehensive digital library platform built with Flask, PostgreSQL, and Docker. The application provides a modern, web-based interface for managing and reading digital books with user authentication, reading progress tracking, and administrative features.

## 📚 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### User Management
- **User Registration & Authentication**: Secure user signup and login system
- **Profile Management**: Complete user profile with personal information
- **Role-based Access Control**: Admin and regular user roles
- **Session Management**: Secure session handling with Flask-Login

### Book Management
- **Digital Library**: Comprehensive collection of books
- **PDF Reading**: In-browser PDF viewing capabilities
- **Book Metadata**: Detailed information including author, translator, description, genre
- **Cover Images**: Visual book representation with cover images
- **Search & Filter**: Advanced book discovery features

### Reading Experience
- **Reading Progress Tracking**: Automatic progress saving and resumption
- **Bookshelf Management**: Personal bookshelf for each user
- **Page Tracking**: Last read page remembering functionality
- **Progress Percentage**: Visual progress indicators

### Administrative Features
- **Admin Dashboard**: Comprehensive admin panel for system management
- **User Management**: Admin capabilities for user administration
- **Book Management**: Add, edit, and manage book collections
- **Data Import**: CSV and SQL file upload capabilities
- **System Monitoring**: Database administration through pgAdmin

## 🏗️ Architecture

The application follows a microservices architecture with the following components:

### Core Services
- **bookapp_web**: Flask web application (Port 5000)
- **bookapp_db**: PostgreSQL database (Port 5432)
- **bookapp_pgadmin**: pgAdmin4 for database management (Port 8080)

### Technology Stack
- **Backend**: Python 3.9+, Flask 2.0+
- **Database**: PostgreSQL 13+
- **Frontend**: HTML5, CSS3, JavaScript, Jinja2 Templates
- **Authentication**: Flask-Login, WTForms
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes ready
- **Cloud Platform**: Google Cloud Platform (GCP)

## 📋 Prerequisites

### Local Development
- Python 3.11 or higher
- Docker & Docker Compose
- Git

### Cloud Deployment
- Google Cloud SDK
- Kubernetes CLI (kubectl)
- Docker Hub or Google Container Registry access

## 🚀 Installation

### Method 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/GuptaNaman1998/book-app.git
   cd book-app
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Web Application: http://localhost:5000
   - pgAdmin: http://localhost:8080
   - Database: localhost:5432

### Method 2: Manual Setup

1. **Set up the database**
   ```bash
   # Start PostgreSQL container
   docker run -d --name bookapp_db \
     -e POSTGRES_USER=admin \
     -e POSTGRES_PASSWORD=secret \
     -e POSTGRES_DB=bookapp \
     -p 5432:5432 postgres:latest
   ```

2. **Set up the web application**
   ```bash
   cd bookapp_web
   pip install -r requirements.txt
   export SQLALCHEMY_DATABASE_URI="postgresql://admin:secret@localhost:5432/bookapp"
   python app/app.py
   ```

3. **Initialize the database**
   ```bash
   # Run the init.sql script to populate initial data
   psql -h localhost -U admin -d bookapp -f init.sql
   ```

## 🎯 Usage

### Default Admin Accounts
The application comes with pre-configured admin accounts:

| Username | Email | Password | Role |
|----------|-------|----------|------|
| Jane_Doe | Jane_Doe@admin.com | abcd1234 | Admin |
| John_doe | John_doe@admin.com | abcd1234 | Admin |
| Naman_Gupta | Naman_Gupta@admin.com | abcd1234 | Admin |

### Getting Started
1. Visit http://localhost:5000
2. Sign up for a new account or login with admin credentials
3. Browse the digital library
4. Start reading books and track your progress

### Available Routes
- `/` - Home/Signup page
- `/login` - User login
- `/bookshelf` - Personal bookshelf
- `/book/<book_id>` - Book reading interface
- `/book_details/<book_id>` - Book information page
- `/profile` - User profile management
- `/admin` - Admin dashboard (admin only)
- `/current_user` - Current user information
- `/docs` - API documentation

## 📖 Book Collection

The platform features an extensive collection of books written by Various Authors:

### Drama
- **Romeo and Juliet** by William Shakespeare is a tragedy likely written during the late 16th century. The play centers on the intense love affair between two young lovers, Romeo Montague and Juliet Capulet, whose families are embroiled in a bitter feud.

### 
- **Moby Dick; Or, The Whale** by Herman Melville is a novel written in the mid-19th century. The story follows Ishmael, a sailor on a whaling voyage, who seeks adventure and escape from his gloomy life on land. As he navigates his way through the town, he is introduced to Queequeg, a tattooed harpooner with a mysterious past, setting the stage for a unique friendship that unfolds amidst the backdrop of whaling adventures.
- **Pride and Prejudice** by Jane Austen is a classic novel written in the early 19th century. The story delves into themes of love, social class, and individual agency, largely revolving around the life of Elizabeth Bennet, one of five sisters from a modest but genteel family navigating the complex social landscape of Regency England.

All books include:
- High-quality ebook versions
- Professional cover images
- Detailed descriptions
- Author and translator information
- Publication dates and genre classification

## 🗄️ Database Schema

### User Table
```sql
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    gender VARCHAR(10),
    address TEXT,
    is_admin BOOLEAN DEFAULT FALSE
);
```

### Book Table
```sql
CREATE TABLE book (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) UNIQUE NOT NULL,
    author VARCHAR(100) NOT NULL,
    translator VARCHAR(100),
    description VARCHAR(1000),
    pdf_loc VARCHAR(100),
    cover_img_loc VARCHAR(100),
    published_on DATE,
    genre VARCHAR(100)
);
```

### Reading Progress Table
```sql
CREATE TABLE reading_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES user(id),
    book_id INTEGER REFERENCES book(id),
    last_read_page INTEGER,
    progress_percentage FLOAT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Deployment

### Google Cloud Platform Deployment

The application is configured for GCP deployment with the provided `deploy.sh` script:

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

#### Deployment Process:
1. **Authentication**: Google Cloud authentication
2. **Artifact Registry**: Creates Docker repository
3. **Container Building**: Builds all service containers
4. **Image Push**: Pushes images to Google Container Registry
5. **Kubernetes Cluster**: Creates GKE cluster
6. **Service Deployment**: Deploys services to Kubernetes

#### Kubernetes Manifests:
- `bookapp_db-deployment.yaml`: Database deployment configuration
- `bookapp_web-deployment.yaml`: Web application deployment
- `bookapp_pgadmin-deployment.yaml`: pgAdmin deployment
- `bookapp_cert.yaml`: SSL certificate configuration

### Environment Configuration

#### Production Environment Variables:
```env
SQLALCHEMY_DATABASE_URI=postgresql://admin:secret@bookapp_db:5432/bookapp
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret
POSTGRES_DB=bookapp
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin
```

## ⚙️ Configuration

### Docker Compose Configuration
The `docker-compose.yml` file defines three services:

#### Database Service (bookapp_db)
- **Image**: PostgreSQL latest
- **Port**: 5432
- **Credentials**: admin/secret
- **Persistent Storage**: bookapp-db-data volume

#### Web Application Service (bookapp_web)
- **Port**: 5000
- **Dependencies**: bookapp_db
- **Auto-restart**: Enabled
- **Network**: bookapp-network

#### pgAdmin Service (bookapp_pgadmin)
- **Port**: 8080
- **Credentials**: admin@example.com/admin
- **Persistent Storage**: bookapp-pgadmin-data volume

### Security Features
- **Password Hashing**: Secure password storage
- **Session Management**: Flask session security
- **CSRF Protection**: WTForms CSRF tokens
- **Input Validation**: Form validation and sanitization
- **SQL Injection Prevention**: SQLAlchemy ORM protection

## 🛠️ Development

### Project Structure
```
containerized-flask-ebook-app/
├── bookapp_web/                 # Flask web application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── app.py              # Main application file
│       ├── static/             # Static assets
│       │   ├── images/         # Book cover images
│       │   └── pdfs/           # PDF book files
│       └── templates/          # HTML templates
├── bookapp_db/                 # Database configuration
│   └── Dockerfile
├── bookapp_pgadmin/            # pgAdmin configuration
│   └── Dockerfile
├── docker-compose.yml          # Docker Compose configuration
├── init.sql                   # Database initialization
├── deploy.sh                  # GCP deployment script
└── README.md                  # Documentation
```

### Local Development Setup

1. **Clone and setup**
   ```bash
   git clone https://github.com/GuptaNaman1998/book-app.git
   cd book-app
   ```

2. **Development environment**
   ```bash
   cd bookapp_web
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database setup**
   ```bash
   docker run -d -p 5432:5432 -e POSTGRES_DB=bookapp -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=secret postgres:latest
   ```

4. **Run application**
   ```bash
   export SQLALCHEMY_DATABASE_URI="postgresql://admin:secret@localhost:5432/bookapp"
   python app/app.py
   ```

### Adding New Books

1. **Add book files**:
   - Place PDF in `bookapp_web/app/static/pdfs/`
   - Place cover image in `bookapp_web/app/static/images/`

2. **Update database**:
   ```sql
   INSERT INTO book (title, author, translator, description, pdf_loc, cover_img_loc, published_on, genre)
   VALUES ('Title', 'Author', 'Translator', 'Description', '/static/pdfs/file.pdf', '/static/images/cover.png', 'YYYY-MM-DD', 'Genre');
   ```

### Testing

The application includes comprehensive error handling and validation:
- Form validation using WTForms
- Database connection error handling
- File upload validation
- User authentication verification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add documentation for new features
- Test thoroughly before submitting PRs

## 📝 API Endpoints

### Authentication
- `POST /signup` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Books
- `GET /bookshelf` - User's personal bookshelf
- `GET /book/<id>` - Read specific book
- `GET /book_details/<id>` - Book details and metadata

### User Management
- `GET /profile` - User profile page
- `POST /profile` - Update user profile
- `GET /current_user` - Current user information

### Administration
- `GET /admin` - Admin dashboard (admin only)
- `POST /admin/upload` - Upload CSV/SQL files (admin only)

## 🔧 Troubleshooting

### Common Issues

#### Database Connection
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs bookapp_db
```

#### Application Errors
```bash
# Check web application logs
docker logs bookapp_web

# Access application shell
docker exec -it bookapp_web bash
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :5000
netstat -tulpn | grep :5432
netstat -tulpn | grep :8080
```

### Performance Optimization
- Use connection pooling for database
- Implement caching for static content
- Optimize PDF loading for better user experience
- Regular database maintenance and indexing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask Community** - For the excellent web framework
- **PostgreSQL Team** - For the robust database system
- **Docker** - For containerization technology

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation and troubleshooting guide

---

**Note**: This application is designed for educational and spiritual content distribution. All books are authored by Saint Praneet Sagar and are included with proper attribution.

**Version**: 1.0.0  
**Last Updated**: August 2025
**Branch**: deployable_code
