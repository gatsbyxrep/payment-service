## Quickstart

Install requirements
```
python -m pip install -r requirements.txt
```

Run tests

```
python -m pytest -v app/tests/
```

if everything is fine, write your configuration data in next files:

docker-compose.yml

app/config/config.yml

app/alembic.ini

Try start docker-compose via
```
docker compose -f 'docker-compose.yml' up -d --build 
```
Now you can use microservice, check troubleshooting topic if here is an issue with database connection

## Troubleshooting
Depends on your Postgres image/Docker configuration you may be have to update your user password in a docker container manually

Example:
```
docker ps
CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS                    PORTS                    NAMES
fd15e6a033e5   postgres   "docker-entrypoint.s…"   20 minutes ago   Up 20 minutes (healthy)   0.0.0.0:5432->5432/tcp payment-service-postgres-1

docker exec -it 7f5b86dfcc0f bash

psql -U <username>

ALTER USER postgres WITH PASSWORD '<your_password>';

exit

```

## TODO
Better configuration managment, we dont really want to specify same data multiple times in different files

Integrational tests