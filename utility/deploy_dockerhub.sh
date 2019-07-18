#!/usr/bin/env bash

#https://docs.travis-ci.com/user/environment-variables/#convenience-variables
#https://docs.travis-ci.com/user/deployment/script/

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

if [ "$TRAVIS_BRANCH" = "development" ]; then
    echo "Deploy da imagem de desenvolvimento..."
    docker push marcelomaia/terceirizadas_backend
fi

if [ "$TRAVIS_BRANCH" = "master" ]; then
    tag="$TRAVIS_TAG"
    if [ -n "$tag" ]; then
        echo "Deploy da imagem de produção..."
        docker tag marcelomaia/terceirizadas_backend:latest marcelomaia/terceirizadas_backend:$tag
        docker push marcelomaia/terceirizadas_backend:$tag
    fi
fi

