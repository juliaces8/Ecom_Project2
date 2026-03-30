# Ecommerce Capstone Project

## Project Overview
A Django-based ecommerce application featuring automated Sphinx documentation and Docker containerization.

## How to Run (Docker)
1. Build the image: 
   `docker build -t ecom-app .`
2. Run the container and migrate: 
   `docker run -p 8000:8000 ecom-app sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"`
3. Access the site at: `http://localhost:8000`

## Documentation
HTML documentation is pre-generated. 
Navigate to: `docs/_build/html/index.html` to view.