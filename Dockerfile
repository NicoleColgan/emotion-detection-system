FROM python:3.10-slim

# set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the project files
COPY . .

# expose flask port
EXPOSE 5000

# run the flask app
CMD ["python", "server.py"]