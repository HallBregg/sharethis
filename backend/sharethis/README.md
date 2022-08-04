## CI jobs
### tests
```sh
python -m unittest -v
```
or
```shell
docker-compose -f docker-compose.yaml run --rm sharethis python -m unittest -v
```

### flake8
This job should be run in `dev` stage of a Dockerfile.

Command:
```shell
flake8 src
```
or
```shell
docker-compose -f docker-compose.yaml run --rm sharethis flake8 src
```
### mypy
This job should be run in `dev` stage of a Dockerfile.

Command:
```shell
mypy src
```
or
```shell
docker-compose -f docker-compose.yaml run --rm sharethis mypy src
```
