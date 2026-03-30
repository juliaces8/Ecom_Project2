# 1. Use an official Python image
FROM python:3.12-slim

# 2. Prevent Python from writing .pyc files and keep logs clean
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the "home" folder inside the container
WORKDIR /app

# 4. Install libraries first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy entire Django project into the container
COPY . .

# 6. Open the port Django uses
EXPOSE 8000

# 7. Start the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]