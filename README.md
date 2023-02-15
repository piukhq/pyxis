Performance testing for BPL applications (Polaris, Carina, Vela)

# Database Population:
For local database population, `.env` should contain:
```
DB_CONNECTION_URI=postgresql://<username>:<password>@localhost:5432/postgres?
VAULT_URL=https://bink-uksouth-perf-bpl.vault.azure.net/
POLARIS_DB=perf_bpl_polaris
CARINA_DB=perf_bpl_carina
VELA_DB=perf_bpl_vela
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

The locust task set can also have tags which can be used to alter the user tasks which are run:

i.e locust_performance_testing/user_tasks.py has the following tags:

- `trc_and_refund`, this is for including/excluding user tasks which will additional bpl features, specifically transaction reward cap (trc) and refunds
- `post_random_transaction`, this is for including/excluding user task for sending a randomized transaction value. See locust_performance_testing.user_tasks:post_transaction for more details



## For testing locally or outside of k8s deployment:

`pipenv run locust --host=http://localhost --locustfile=locust_performance_testing/locustfile_dev.py --exclude-tags post_random_transaction`

Note: The --host must be the same as where the tested API is being run. i.e polaris, carina, vela all need to be on the same host

Then, go to http://0.0.0.0:8089 in the browser and configure the user and spawn rate.