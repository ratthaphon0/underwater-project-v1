FROM node:20-alpine
WORKDIR /app

# Cache Layer
COPY package.json package-lock.json* ./
RUN npm install

# Code Layer
COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]