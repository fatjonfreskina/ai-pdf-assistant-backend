# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV ENVIRONMENT=production

# Expose port 8000 to the outside world
EXPOSE 8000

# Set the working directory to the src directory
WORKDIR /app/src

# Run flask when the container launches
CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "9000", "--call", "main:create_app"]
