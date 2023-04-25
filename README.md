Performance testing for BPL cosmos

# Database Population:
For local database population, `.env` should contain:
```
DB_CONNECTION_URI=postgresql://<username>:<password>@localhost:5432/postgres?
VAULT_URL=https://bink-uksouth-perf-bpl.vault.azure.net/
COSMOS_DB=perf_bpl_polaris
```

To run database population (from root dir):
```
python commands.py -t <task name> -d <data configuration>
```
For more information about available parameters:
```
python commands.py --help
```

# Running Performance Tests:
To start up locust, run:

`pipenv run locust --host=https://perf-bpl.sandbox.gb.bink.com --locustfile=PATH_TO_FILE`