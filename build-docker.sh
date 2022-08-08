docker build -f Dockerfile -t cdn-switcher/latest .
docker run -d --name=SG-CDN-Switcher \
           --restart always cdn-switcher/latest
