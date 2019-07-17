#!/usr/bin/env bash

if [ "$TRAVIS_BRANCH" = "development" ]; then
    echo "Deploy da imagem de desenvolvimento..."
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    docker push marcelomaia/terceirizadas_backend
fi



#$TRAVIS_TAG
