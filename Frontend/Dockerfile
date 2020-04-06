FROM node

RUN npm install -g http-server
RUN npm install -g @vue/cli

WORKDIR /app

COPY ./command-center/package*.json ./

RUN npm install

COPY ./command-center ./

RUN npm run build

CMD [ "http-server", "dist" ]
