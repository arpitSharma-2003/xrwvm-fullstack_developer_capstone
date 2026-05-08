FROM node:18.12.1-bullseye-slim

RUN npm install -g npm@9.1.3

WORKDIR /app

# 1) Copy package files first (better caching)
COPY package*.json ./

# 2) Install dependencies (THIS WAS MISSING)
RUN npm ci || npm install

# 3) Copy the rest of the app
COPY . .

EXPOSE 3050

CMD ["node", "app.js"]