docker stop kakapo
docker build -t kakapo_image .
docker rm kakapo
docker run --name kakapo -p 3000:3000 kakapo_image