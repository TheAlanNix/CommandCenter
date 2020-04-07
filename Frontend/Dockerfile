# Build
FROM node as build

WORKDIR /app

COPY ./command-center/package*.json ./

RUN npm install

COPY ./command-center .

RUN npm run build

# Prod
FROM nginx as production

COPY --from=build /app/dist /usr/share/nginx/html
