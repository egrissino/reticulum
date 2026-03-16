#!/bin/bash

USER=$(whoami)
ARCH=$(arch)

if [[ "$ARCH" -eq "x86_64" ]]; then
    ARCH=amd64
fi

app=reticulum
retworkspace=/home/ret
localworkspace=$(pwd)/../ret
image=$app-server
container=$app-server-$USER
network=$app-net

old_container=$(docker ps -q -f name=$container)

if [[ ! -z "$old_container" ]]; then
    docker kill $container
    docker remove $container
    docker rmi $image
fi

old_network=$(docker network inspect $network)
if [[ ! $old_network ]]; then
    docker network create --driver bridge $network
fi

docker buildx build \
    --platform=linux/$ARCH \
    --build-arg USERNAME=$USER \
    -t "$image:latest" .

docker run -d \
    --name="$container" \
    --volume $localworkspace:$retworkspace \
    --network $network \
    --publish 61549:61549 \
    --interactive \
    --rm \
    -t $image:latest