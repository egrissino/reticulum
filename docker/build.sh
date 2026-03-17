#!/bin/bash


echo "= = = = = = = = = = = = = = = = = = = = = = = = = = ="
echo "              Reticulum P2P Comms"
echo "= = = = = = = = = = = = = = = = = = = = = = = = = = ="
echo
echo "1. Build Reticulum Isolated Runtime (RIR)"
echo "2. Run Send/Receive script"
echo "3. Enter shared signal - negotiated out-of-band"
echo "4. Enter Recipients Encrypted Destination Hash (EDH)"
echo "5. Wait for link to initiate and begin comms"
echo

echo "Step 1: Build RIR"

USER=$(whoami)
ARCH=$(arch)

if [[ "$ARCH" -eq "x86_64" ]]; then
    ARCH=amd64
fi

echo "  Build System: ${ARCH}"
echo "  User: $USER"

app=reticulum
retworkspace=/home/ret
localworkspace=$(pwd)/../ret
image=$app-server
container=$app-server-$USER
network=$app-net

echo "  RIR-name: ${container} from image: ${image}"

old_container=$(docker ps -q -f name=$container)
if [[ ! -z "$old_container" ]]; then
    echo "  Prune expired RIR instances"
    docker kill $container
    docker remove $container
    docker rmi $image
fi

echo "  Adding Network: ${network}"
old_network=$(docker network inspect $network)
if [[ ! $old_network ]]; then
    docker network create --driver bridge $network
fi

echo "  Build RIR..."

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

echo "  -> RIR ready"