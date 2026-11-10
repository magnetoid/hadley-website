FROM nginx:1.27-alpine
RUN apk add --no-cache python3 supervisor ca-certificates
COPY contact_server.py /app/contact_server.py
COPY supervisord.conf /etc/supervisord.conf
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
COPY default.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY robots.txt sitemap.xml /usr/share/nginx/html/
COPY assets/ /usr/share/nginx/html/assets/
COPY about/ /usr/share/nginx/html/about/
COPY services/ /usr/share/nginx/html/services/
COPY experience/ /usr/share/nginx/html/experience/
COPY insights/ /usr/share/nginx/html/insights/
COPY team/ /usr/share/nginx/html/team/
COPY contact/ /usr/share/nginx/html/contact/
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1:3000/ || exit 1
