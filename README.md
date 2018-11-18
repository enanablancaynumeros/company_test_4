# inventory_management

## Installation
Having docker-compose installed in your python virtual environment will be sufficient to
run the tests inside docker containers, otherwise:
1) Create a new virtual environment and run `pip install -r requirements.txt`.
2) run `make build` to ensure docker is correctly installed and you can build the images

## Tests
Run `make tests` to run the behave tests inside the docker containers.

For debugging you can also run `make behave_locally`  which will be talking to the DB 
container through the host and running under the same process.


## Running the app

Running `make up` will bring up the DB, the api and a migration container that will
create the DB and will apply the first migration.
 