FROM node:22-alpine AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./frontend/

WORKDIR /app/frontend

RUN npm ci

COPY frontend /app/frontend

# Construir versión de producción
RUN npm run build

# --- Etapa de runtime: servir estático con Vite preview ---
FROM node:22-alpine AS runtime

WORKDIR /app/frontend

ENV NODE_ENV=production

COPY --from=build /app/frontend /app/frontend

EXPOSE 8080

# VITE_API_URL se pasa desde docker-compose para apuntar al backend
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "8080"]

