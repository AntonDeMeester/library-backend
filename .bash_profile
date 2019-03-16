docker run -ti --env-file .env -v ~/.aws/:/root/.aws --rm library bash -c "pipenv install && pipenv shell"

docker run --env-file .env -v cd:/var/task --rm library bash -c "cd /var/task && pipenv shell && pipenv install && zappa update dev"