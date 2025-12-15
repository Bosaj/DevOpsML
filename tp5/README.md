# Flask Docker Application - TP5

A comprehensive full-stack web application built with Flask, SQLAlchemy, and Docker.

## Features

- User management system (CRUD operations)
- Contact form with database storage
- RESTful API endpoints
- SQLite database integration
- Responsive design
- Flash messaging system
- Docker containerization

## Technologies

- Python 3.11
- Flask 3.0
- SQLAlchemy
- SQLite
- Docker
- HTML5/CSS3
- JavaScript

## Installation

### Using Docker (Recommended)

Build and run with docker-compose
docker-compose up --build

Or build manually
docker build -t flask-app .
docker run -d -p 5000:5000 --name flask-app flask-app

text

### Manual Installation

Install dependencies
pip install -r requirements.txt

Run the application
python app.py

text

## Usage

Access the application at `http://localhost:5000`

### API Endpoints

- `GET /api/users` - Get all users in JSON format
- `GET /api/stats` - Get application statistics

## Project Structure

tp5/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── templates/
└── static/

text

## Author

TP5 Docker Exercise - 2025