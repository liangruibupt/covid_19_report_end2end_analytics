
# Running on China region

## PyAthena for AWS China region

The athena endpoint in China region is different from Global region. 

- [China (Ningxia) Region Endpoints](https://docs.amazonaws.cn/en_us/general/latest/gr/cnnorthwest_region.html) athena.cn-northwest-1.amazonaws.com.cn
- [China (Beijing) Region Endpoints](https://docs.amazonaws.cn/en_us/general/latest/gr/cnnorth_region.html) athena.cn-north-1.amazonaws.com.cn

So below code can not work in China region:

https://github.com/laughingman7743/PyAthena/blob/master/pyathena/sqlalchemy_athena.py#L233

You will encounter the error:

```bash
# awsathena+rest URI
botocore.exceptions.EndpointConnectionError: Could not connect to the endpoint URL: "https://athena.athena.cn-northwest-1.amazonaws.com.cn.amazonaws.com/"
```
The issue https://github.com/laughingman7743/PyAthena/issues/134 has been tracked.

The workaround for sqlalchemy_athena.py

```bash
# 1. update https://github.com/laughingman7743/PyAthena/blob/master/pyathena/sqlalchemy_athena.py#L233 as below
'region_name': re.sub(r'^athena\.([a-z0-9-]+)\.amazonaws\.(com.cn|com)$', r'\1', url.host),
# 2. upload the code to public storage, such as github

# 3. Edit the Dockerfile to replace the new sqlalchemy_athena.py
USER root
RUN mv /usr/local/lib/python3.6/site-packages/pyathena/sqlalchemy_athena.py /usr/local/lib/python3.6/site-packages/pyathena/sqlalchemy_athena.py.global
RUN curl -o /usr/local/lib/python3.6/site-packages/pyathena/sqlalchemy_athena.py https://raw.githubusercontent.com/liangruibupt/covid_19_report_end2end_analytics/master/script/china-region-pyathena-sqlalchemy_athena.py

# Rebuild and Restart superset
docker-compose build
docker-compose up
```


## Pyathenajdbc for AWS China region

The athena endpoint in China region is different from Global region. 

- [China (Ningxia) Region Endpoints](https://docs.amazonaws.cn/en_us/general/latest/gr/cnnorthwest_region.html) athena.cn-northwest-1.amazonaws.com.cn
- [China (Beijing) Region Endpoints](https://docs.amazonaws.cn/en_us/general/latest/gr/cnnorth_region.html) athena.cn-north-1.amazonaws.com.cn

So below code can not work in China region:

https://github.com/laughingman7743/PyAthenaJDBC/blob/master/pyathenajdbc/sqlalchemy_athena.py#L120

You will encounter the error:

```bash
# awsathena+jdbc URI error
superset_1         | DEBUG:pyathenajdbc.connection:JVM args: ['-server', '-Djava.class.path=/usr/local/lib/python3.6/site-packages/pyathenajdbc/AthenaJDBC42_2.0.9.jar', '-Dlog4j.configuration=file:/usr/local/lib/python3.6/site-packages/pyathenajdbc/log4j.properties']
superset_1         | ERROR:superset.views.core:Unexpected error java.sql.SQLException: [Simba][AthenaJDBC](100131) An error has been thrown from the AWS SDK client. Unable to execute HTTP request: athena.athena.cn-northwest-1.amazonaws.com.cn.amazonaws.com: Name or service not known [Execution ID not available]
```
The issue https://github.com/laughingman7743/PyAthenaJDBC/issues/97 has been tracked.

The workaround for sqlalchemy_athena.py

```bash
# 1. update https://github.com/laughingman7743/PyAthenaJDBC/blob/master/pyathenajdbc/sqlalchemy_athena.py#L120 as below
'region_name': re.sub(r'^athena\.([a-z0-9-]+)\.amazonaws\.(com.cn|com)$', r'\1', url.host),
# 2. upload the code to public storage, such as github

# 3. Edit the Dockerfile to replace the new sqlalchemy_athena.py
USER root
RUN mv /usr/local/lib/python3.6/site-packages/pyathenajdbc/sqlalchemy_athena.py /usr/local/lib/python3.6/site-packages/pyathenajdbc/sqlalchemy_athena.py.global
RUN curl -o /usr/local/lib/python3.6/site-packages/pyathenajdbc/sqlalchemy_athena.py https://raw.githubusercontent.com/liangruibupt/covid_19_report_end2end_analytics/master/script/china-region-pyathenajdbc-sqlalchemy_athena.py

EndpointOverride

# Rebuild and Restart superset
docker-compose build
docker-compose up
```


## Example Superset SQLAlchemy URI when create new data source
**NOTE: For awsathena+jdbc, you need specify the EndpointOverride=<athena-china-region-endpoint>**
- Ningxia region: EndpointOverride=athena.cn-northwest-1.amazonaws.com.cn
- Beijing region: EndpointOverride=athena.cn-north-1.amazonaws.com.cn
```
awsathena+jdbc://:@athena.cn-northwest-1.amazonaws.com.cn/covid19?s3_staging_dir=s3://covid-19-output-data-zhy/&EndpointOverride=athena.cn-northwest-1.amazonaws.com.cn
awsathena+rest://:@athena.cn-northwest-1.amazonaws.com.cn:443/covid19?s3_staging_dir=s3://covid-19-output-data-zhy/

```