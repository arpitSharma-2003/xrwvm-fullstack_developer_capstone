FROM node:18.12.1-bullseye-slim

RUN npm install -g npm@9.1.3

WORKDIR /

COPY package.json /package.json
COPY app.js /app.js
COPY inventory.js /inventory.js
COPY data/car_records.json /car_records.json

COPY . .

EXPOSE 3050

CMD ["node", "app.js"]