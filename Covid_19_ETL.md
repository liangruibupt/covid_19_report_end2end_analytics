## Step 1. Crappifiyng the dataset
Given the goal is to practice with ETL pipelines, so add the mess on downloaded the dataset.
1. Add id column
2. Randomly add duplicated rows
3. Add Random-Field-{i}: {i}

```bash
# Download Jupyter Notebook
curl -O https://raw.githubusercontent.com/FraPochetti/KagglePlaygrounds/master/COVID-19-crappification.ipynb

source venv/bin/activate
pip install numpy scipy matplotlib ipython jupyter pandas sympy nose sqlalchemy psycopg2-binary boto3 tqdm
jupyter notebook COVID-19-crappification.ipynb --port 8888 --no-browser

# Modify notebook code based on latest dataset schema
def crappify_province(x):
    if x['Province/State'] is None: x['Province/State'] = random.choice(['NULL', '', 'missing', '--']) 
    return x

raw data S3 bucket: covid-19-raw-data
output data S3 bucket: covid-19-output-data

# Run the notebook to Crappifiy the data

# Sample Crappifiyng data
{'Province/State': 'Jiangxi', 'Country/Region': 'China', 'Lat': 27.614, 'Long': 115.7221, 'Date': '2020-01-30', 'Confirmed': 162, 'Deaths': 0, 'Recovered': 5, 'id': 2122, 'Random-Field-0': 0, 'Random-Field-1': 1, 'Random-Field-2': 2, 'Random-Field-3': 3, 'Random-Field-4': 4, 'Random-Field-5': 5, 'Random-Field-6': 6, 'Random-Field-7': 7, 'Random-Field-8': 8, 'Random-Field-9': 9}
```

## Step 2. Crawl S3 input with Glue
1. Create AWS Glue Crawler covid19 point to covid-19-raw-data s3 bucket
2. covid_19_raw_data table created within the Glue Data Catalog. 
As you can see the Glue Crawler correctly identified number of objects in S3 and parsed the following JSON fields out of schema.

![media/raw-data-crawler.png](media/raw-data-crawler.png)

## Step 3. Run ETL with Glue
1. Select only the fields we are interested in, e.g. Confirmed, Country/Region, Date, Deaths, Lat, Long, Province/State, Recovered, id
2. Removing any Random-Field-* (undo the add_fields function).
3. Fix the Date formatting (undo the crappify_date function).
4. Homogenize the null values of Province-State (undo the crappify_province function).
5. Homogenize Confirmed, Recovered and Deaths in case the value on any of those fields equals 0 (undo the crappify_zeros function).

![media/data-etl.png](media/data-etl.png)

- If you want to debug your ETL job, run/test code on-demand, you can create Glue `Dev Endpoint` 
![media/glue-dev-endpoint.png](media/glue-dev-endpoint.png)
- If you want to connect to the Glue Data Catalog and run/test code on-demand in Jupyter Notebook, you can create create a `Notebook` associate with a `Dev Endpoint`.
![media/glue-dev-endpoint-sm-notebook.png](media/glue-dev-endpoint-sm-notebook.png)

Modify the script based on you requirement or you can download [Sample ETL Spark script](script/COVID-19_glue_etl_job_pyspark.py) paste to Glue ETL job.


## Step 4. Crawl ETL output with Glue 
1. Create AWS Glue Crawler covid19-output point to covid-19-output-data s3 bucket
2. covid-19-output-data table created within the Glue Data Catalog. 
As you can see the Glue Crawler correctly identified number of objects in S3 and parsed the following JSON fields out of schema.
![media/output-data-crawler.png](media/output-data-crawler.png)

## Step 5. Query Glue Catalog with Athena
```bash
SELECT * FROM "covid19"."covid_19_raw_data" limit 10;

SELECT * FROM "covid19"."covid_19_output_data" limit 10;

CREATE TABLE covid19_athena
as select "province/state", "country/region", "lat", "long",
 cast(date as TIMESTAMP) as report_time, "confirmed", "deaths", "recovered"
from (
select t.*,
    row_number() over (partition by id order by date) as r
from "covid19"."covid_19_output_data" t)
where r = 1

SELECT count(*) FROM "covid19"."covid19_athena";
19018

SELECT * FROM "covid19"."covid19_athena" limit 10;

```

## Step 6. Visualize with Superset
1. Follow up [Superset quick start guide](Install_Superset.md) to install and configure Superset
2. [Familar with PyAthena](PyAthena-sample.md) to verify the Superset host can connect to Athena
3. Create new covid19 database on Superset Web UI
4. [The connection string for Athena](https://superset.apache.org/installation.html#aws-athena)
```bash
# jdbc uri
awsathena+jdbc://{aws_access_key_id}:{aws_secret_access_key}@athena.{region_name}.amazonaws.com/{schema_name}?s3_staging_dir=s3%3A//{your-s3-bucket-name}/
awsathena+jdbc://{aws_access_key_id}:{aws_secret_access_key}@athena.{region_name}.amazonaws.com/{schema_name}?s3_staging_dir=s3%3A//{your-s3-bucket-name}/&driver_path=/drivers/AthenaJDBC41_2.0.6.jar
# Use the instance profile
awsathena+jdbc://:@athena.{region_name}.amazonaws.com/{schema_name}?s3_staging_dir=s3%3A//{your-s3-bucket-name}/

# PyAthena uri
awsathena+rest://{aws_access_key_id}:{aws_secret_access_key}@athena.{region_name}.amazonaws.com:443/{schema_name}?s3_staging_dir=s3%3A//{your-s3-bucket-name}
# Use the instance profile
awsathena+rest://:@athena.{region_name}.amazonaws.com:443/{schema_name}?s3_staging_dir=s3%3A//{your-s3-bucket-name}

# For example:
#awsathena+jdbc://:@athena.us-east-1.amazonaws.com/covid19?s3_staging_dir=s3://covid-19-output-data/
#awsathena+rest://:@athena.us-east-1.amazonaws.com:443/covid19?s3_staging_dir=s3://covid-19-output-data/

#
```
5. Superset connect to `covid19_athena` table within the Glue Data Catalog to pivoting the data on different dimensions

![superset-dashboard](media/superset-dashboard-covid.png)
![superset-dashboard2](media/superset-dashboard-covid2.png)


## Resource
- [covid-19-end-to-end-analytics-with-aws-glue-athena-and-quicksight](https://francescopochetti.com/covid-19-end-to-end-analytics-with-aws-glue-athena-and-quicksight/)

- [query-and-visualize-data-from-amazon-athena-with-superset](https://dev.classmethod.jp/articles/query-and-visualize-data-from-amazon-athena-with-superset/)

- [PyAthena](https://github.com/laughingman7743/PyAthena#sqlalchemy)

## Appndix
- [Using Athena with the JDBC Driver](https://docs.aws.amazon.com/athena/latest/ug/connect-with-jdbc.html)
```bash
[ec2-user@ incubator-superset]$ mkdir driver
[ec2-user@ incubator-superset]$ cd driver/
[ec2-user@ driver]$ curl -O https://s3.amazonaws.com/athena-downloads/drivers/JDBC/SimbaAthenaJDBC_2.0.9/AthenaJDBC42_2.0.9.jar
[ec2-user@ driver]$ curl -O https://athena-downloads.s3.amazonaws.com/drivers/JDBC/SimbaAthenaJDBC_2.0.9/AthenaJDBC41_2.0.9.jar
```

- Athena sample query
```sql
CREATE EXTERNAL TABLE `covid_table` (
  `province/state` string, 
  `country/region` string, 
  `lat` double, 
  `long` double, 
  `report_date` string, 
  `confirmed` bigint, 
  `deaths` bigint, 
  `recovered` bigint
  )           
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://covid-19-output-data-zhy/' ;


SELECT * FROM "covid19"."covid_table" limit 10;

CREATE TABLE covid19_table_date
as select "province/state", "country/region", "lat", "long",
 date_parse(report_date, '%m-%d-%Y') as r_date, "confirmed", "deaths", "recovered"
from (
select t.*
from "covid19"."covid_table" t)


SELECT * FROM "covid19"."covid19_table_date" limit 10;
```