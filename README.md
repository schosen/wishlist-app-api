# wishlist-app-api
Wishlist API

Create migrations files:
```
docker-compose run --rm app sh -c "python manage.py makemigrations"
```
Run the wait for database to build and then run migrate locally

```
docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"
```

Run test locally
```
docker-compose run --rm app sh -c "python manage.py test"
```

Run linting locally
```
docker-compose run --rm app sh -c "python manage.py wait_for_db && flake8"
```
