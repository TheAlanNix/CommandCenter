# Compile the page assets
FROM node AS build-env

COPY ./frontend /app

WORKDIR /app/frontend

RUN npm install
RUN npm run build

# Build for production
FROM python:3

COPY --from=build-env /app/dist /app/frontend/dist
COPY ./modules /app/modules
COPY ./requirements.txt /app
COPY ./app.py /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "app.py"]
