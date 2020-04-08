import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
# @type: DataSource
# @args: [database = "covid19", table_name = "covid_19_raw_data", transformation_ctx = "datasource0"]
# @return: datasource0
# @inputs: []
datasource0 = glueContext.create_dynamic_frame.from_catalog(
    database="covid19", table_name="covid_19_raw_data", transformation_ctx="datasource0")
# @type: ApplyMapping
# @args: [mapping = [("province/state", "string", "province/state", "string"), ("country/region", "string", "country/region", "string"), ("lat", "double", "lat", "double"), ("long", "double", "long", "double"), ("date", "string", "date", "string"), ("confirmed", "string", "confirmed", "string"), ("deaths", "string", "deaths", "string"), ("recovered", "string", "recovered", "string"), ("id", "int", "id", "int")], transformation_ctx = "applymapping1"]
# @return: applymapping1
# @inputs: [frame = datasource0]
applymapping1 = ApplyMapping.apply(frame=datasource0, mappings=[("province/state", "string", "province/state", "string"), ("country/region", "string", "country/region", "string"), ("lat", "double", "lat", "double"), ("long", "double", "long", "double"), (
    "date", "string", "date", "string"), ("confirmed", "string", "confirmed", "string"), ("deaths", "string", "deaths", "string"), ("recovered", "string", "recovered", "string"), ("id", "int", "id", "int")], transformation_ctx="applymapping1")
# @type: DataSink
# @args: [connection_type = "s3", connection_options = {"path": "s3://covid-19-output-data"}, format = "json", transformation_ctx = "datasink2"]
# @return: datasink2
# @inputs: [frame = applymapping1]
datasink2 = glueContext.write_dynamic_frame.from_options(frame=applymapping1, connection_type="s3", connection_options={
                                                         "path": "s3://covid-19-output-data"}, format="json", transformation_ctx="datasink2")
job.commit()
