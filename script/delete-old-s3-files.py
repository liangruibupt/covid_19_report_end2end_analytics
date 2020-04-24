import boto3
import time
import sys

# todays\'s epoch
_tday = time.time()
# initialize s3 client
s3_client = boto3.client('s3')
bucket_para = [{
    "src_bucket": "covid-19-raw-data-zhy",  # The bucket in US
    "src_prefix": "enigma-jhu/json/"
}, {
    "src_bucket": "covid-19-raw-data-zhy",  # The bucket in US
    "src_prefix": "enigma-jhu-timeseries/json/"
},{
    "src_bucket": "covid-19-raw-data-zhy",
    "src_prefix": "static-datasets/json/CountyPopulation/"
},{
    "src_bucket": "covid-19-raw-data-zhy",  # The bucket in US
    "src_prefix": "static-datasets/json/countrycode/"
}, {
    "src_bucket": "covid-19-raw-data-zhy",  # The bucket in US
    "src_prefix": "static-datasets/json/CountyPopulation/"
}, {
    "src_bucket": "covid-19-output-data-zhy",
    "src_prefix": "enigma_jhu_parquet/"
}]
# bucket_para = [{
#     "src_bucket": "covid-19-raw-data-zhy",  # The bucket in US
#     "src_prefix": "enigma-jhu-timeseries/json"
# }, {
#     "src_bucket": "covid-19-raw-data-zhy",  # The bucket in US
#     "src_prefix": "enigma-jhu-timeseries/csv"
# }]


def get_key_info(bucket="my-s3-bucket", prefix="my-s3-key/"):

    print(
        f"Getting S3 Key Name, Size and LastModified from the Bucket: {bucket} with Prefix: {prefix}")

    key_names = []
    file_timestamp = []
    file_size = []
    kwargs = {"Bucket": bucket, "Prefix": prefix}
    while True:
        response = s3_client.list_objects_v2(**kwargs)
        objs = response["Contents"]
        for obj in objs:
            # exclude directories/folder from results. Remove this if folders are to be removed too
            if "." in obj["Key"]:
                key_names.append(obj["Key"])
                file_timestamp.append(obj["LastModified"].timestamp())
                file_size.append(obj["Size"])
        try:
            kwargs["ContinuationToken"] = response["NextContinuationToken"]
        except KeyError:
            break

    key_info = {
        "key_path": key_names,
        "timestamp": file_timestamp,
        "size": file_size
    }
    print(f'All Keys {key_info} in {bucket} with {prefix} Prefix found!')

    return key_info


# get the latest add file from s3 bucket
def get_lastest_obj(bucket="my-s3-bucket", prefix="my-s3-key/"):
    def get_last_modified(obj): return int(obj['LastModified'].strftime('%s'))

    kwargs = {"Bucket": bucket, "Prefix": prefix}
    objs = s3_client.list_objects_v2(**kwargs)['Contents']
    last_added = [obj['Key'] for obj in sorted(objs, key=get_last_modified, reverse=True)][0]

    print(
        f'Found latest object {last_added} in {bucket} with {prefix} Prefix found!')
    return last_added

# connect to s3 and delete the file
def delete_s3_file(file_path, bucket="my-s3-bucket"):
    print(f"Deleting {file_path} in {bucket}")
    s3_client.delete_object(Bucket=bucket, Key=file_path)
    return True


# check size deleted
def _total_size_dltd(size, _file_size):
    _file_size.append(size)
    # convert from bytes to mebibytes
    _del_size = round(sum(_file_size)/1.049e+6, 2)
    return _del_size


if __name__ == "__main__":
    try:
        for bucket_para in bucket_para:
            _file_size = []  # just to keep track of the total savings in storage size
            _del_size = 0
            src_bucket = bucket_para['src_bucket']
            src_prefix = bucket_para['src_prefix']
            print(f"Getting S3 Bucket: {src_bucket} with Prefix: {src_prefix}")
            s3_file = get_key_info(src_bucket, src_prefix)
            latest_file = get_lastest_obj(src_bucket, src_prefix)
            for counter, file_obj in enumerate(s3_file['key_path']):
                if file_obj == latest_file:
                    print(f'Skip the latest file {latest_file}')
                else:
                    print(f'delete file {file_obj}')
                    delete_s3_file(file_obj, src_bucket)
                    _del_size = _total_size_dltd(s3_file["size"][counter], _file_size)
            print(f"Delete the old files in S3 Bucket: {src_bucket} with Prefix: {src_prefix} with total size: {_del_size} MiB")
    except:
        print("failure:", sys.exc_info()[1])
