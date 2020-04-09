
# Running on China region

## PyAthena for AWS China region

The athena endpoint in China region is different from Global region. So below code can not work in China region:

https://github.com/laughingman7743/PyAthena/blob/master/pyathena/sqlalchemy_athena.py#L233

So you will encounter the error:

```bash
botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL: "https://athena.athena.cn-northwest-1.amazonaws.com.cn.amazonaws.com/"
```
- [China (Ningxia) Region Endpoints](https://docs.amazonaws.cn/en_us/general/latest/gr/cnnorthwest_region.html) athena.cn-northwest-1.amazonaws.com.cn
- [China (Beijing) Region Endpoints](https://docs.amazonaws.cn/en_us/general/latest/gr/cnnorth_region.html) athena.cn-north-1.amazonaws.com.cn

The workaround for sqlalchemy_athena.py

```bash
# 1. update https://github.com/laughingman7743/PyAthena/blob/master/pyathena/sqlalchemy_athena.py#L233 as below
'region_name': re.sub(r'^athena\.([a-z0-9-]+)\.amazonaws\.(com.cn|com)$', r'\1', url.host),
# 2. upload the code to public storage, such as github

# 3. Edit the Dockerfile to replace the new sqlalchemy_athena.py
USER root
RUN mv /usr/local/lib/python3.6/site-packages/pyathena/sqlalchemy_athena.py /usr/local/lib/python3.6/site-packages/pyathena/sqlalchemy_athena.py.global
RUN curl -o /usr/local/lib/python3.6/site-packages/pyathena/sqlalchemy_athena.py https://raw.githubusercontent.com/liangruibupt/covid_19_report_end2end_analytics/master/script/china-region-sqlalchemy_athena.py

# Rebuild and Restart superset
docker-compose build
docker-compose up
```

## Superset SQLAlchemy URI when create new data source
```
awsathena+jdbc://:@athena.cn-northwest-1.amazonaws.com.cn/covid19?s3_staging_dir=s3://covid-19-output-data-zhy/
awsathena+rest://:@athena.cn-northwest-1.amazonaws.com.cn:443/covid19?s3_staging_dir=s3://covid-19-output-data-zhy/

```

## Athena sample query
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