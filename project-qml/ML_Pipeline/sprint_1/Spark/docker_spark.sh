echo "pulling docker compose file"
curl -LO https://raw.githubusercontent.com/bitnami/containers/main/bitnami/spark/docker-compose.yml
echo "building the docker image"
docker compose up
xdg-open https://localhost:8080
