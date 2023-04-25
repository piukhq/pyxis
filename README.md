Performance testing for BPL cosmos

# Database Population:
For local database population, `.env` should contain:
```sh
DB_CONNECTION_URI=postgresql://<username>:<password>@localhost:5432/postgres?
VAULT_URL=https://bink-uksouth-perf-bpl.vault.azure.net/
COSMOS_DB=perf_bpl_cosmos
```

To run database population (from root dir):
```sh
python commands.py -t <task name> -d <data configuration>
```
For more information about available parameters:
```sh
python commands.py --help
```

# Running Performance Tests:
To start up locust, run:

For testing locally, add the following to .env:

```sh
PUBLIC_API_URL=http://localhost:8000/
TRANSACTIONS_API_URL=http://localhost:8002/
ACCOUNTS_API_URL=http://localhost:8003/
LUNA_API_URL=http://localhost:9001
```

Starting the locust test:

```sh
pipenv run locust --host=https://perf-bpl.sandbox.gb.bink.com --locustfile=PATH_TO_FILE
```

Note: The --host must be the same as where the tested APIs is being run
Then, go to http://0.0.0.0:8089 in the browser and configure the user and spawn rate.

Alternatively, to run headless mode:

```sh
pipenv run locust --host=http://localhost --locustfile=locust_performance_testing/locustfile_dev.py --headless --users=1 --spawn-rate=1
```