# The builder image, used to build the virtual environment
FROM python:3.10-slim as builder

RUN apt-get update && apt-get install -y git

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /app

COPY ./src src/
COPY ./sample_data.csv sample_data.csv

# Create output directory for CSV files
RUN mkdir -p output

EXPOSE 8501

CMD ["streamlit", "run", "src/streamlit_app.py", "--server.port=8501", "--theme.base=dark"]