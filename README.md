# Database Population:
For local database population, `.env` should contain:
```
DB_CONNECTION_URI=postgresql://<username>:<password>@localhost:5432/postgres
```

To run database population (from root dir):
```
python commands.py -t <task name> -d <data configuration>
```
For more information about available parameters:
```
python commands.py --help
```