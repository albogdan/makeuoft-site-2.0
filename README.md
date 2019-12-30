# makeuoft-site
MakeUofT 2020 site for Canada's largest makeathon. 

## Installation
Make sure you have Python 3 and pip installed.

In terminal:

```bash

cd .. .. ..
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

You will also need to have [docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) installed, or have a local mysql server running.
## Usage
Activate the virtual environment:
```bash
source venv/bin/activate
```

Start the database:
```bash
docker-compose up -d
```
> `-d` suppresses the output, in can be omitted if you want to check on the database.

Run migrations:
```bash
flask db upgrade
```

Seed the database:
```bash
flask seed seedall
```
> This will cause issues if ran multiple times on the same database. If you want to re-seed your database, first destroy the container with `docker-compose down` and re-create it with `docker-compose up -d`.

Run the application:

```bash
python main.py
```

## Committing
Make changes in a descriptively-named branch, and submit a pull request to this repo. It must be approved by at least one contributor to be merged to master, which is protected. New features should have unit tests.


