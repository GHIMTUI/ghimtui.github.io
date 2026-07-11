# Sử dụng bản node có sẵn ffmpeg cực nhẹ
FROM jrottenberg/ffmpeg:4.4-ubuntu AS ffmpeg
FROM node:18-slim

# Copy ffmpeg từ bản build sang
COPY --from=ffmpeg / /

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

EXPOSE 3000
CMD ["node", "server.js"]
