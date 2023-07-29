FROM nginx:1.19.0-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY privkey.pem /etc/nginx/conf.d
COPY fullchain.pem /etc/nginx/conf.d