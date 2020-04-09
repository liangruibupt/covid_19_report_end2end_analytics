import re


class AthenaDialect():
    def create_connect_args(self, url):
        # Connection string format:
        #   awsathena+rest://
        #   {aws_access_key_id}:{aws_secret_access_key}@athena.{region_name}.amazonaws.com:443/
        #   {schema_name}?s3_staging_dir={s3_staging_dir}&...
        opts = {
            'aws_access_key_id': url.username if url.username else None,
            'aws_secret_access_key': url.password if url.password else None,
            'region_name': re.sub(r'^athena\.([a-z0-9-]+)\.amazonaws\.(com.cn|com)$', r'\1', url.host),
            'schema_name': url.database if url.database else 'default'
        }
        print(opts)
        opts.update(url.query)
        return [[], opts]


class URL():
    pass


_myurl = URL()
_myurl.username = 'foo'
_myurl.password = 'bar'
_myurl.host = 'athena.us-east-1.amazonaws.com'
_myurl.database = 'sample'
_myurl.query = {
    'connection': 'awsathena+jdbc://{aws_access_key_id}:{aws_secret_access_key}@athena.{region_name}.amazonaws.com/{schema_name}'}


_myurl_zhy = URL()
_myurl_zhy.username = 'foo-cn'
_myurl_zhy.password = 'bar-cn'
_myurl_zhy.host = 'athena.cn-northwest-1.amazonaws.com.cn'
_myurl_zhy.database = 'sample'
_myurl_zhy.query = {
    'connection': 'awsathena+jdbc://{aws_access_key_id}:{aws_secret_access_key}@athena.{region_name}.amazonaws.com.cn/{schema_name}'}

_myurl_bjs = URL()
_myurl_bjs.username = 'foo-cn'
_myurl_bjs.password = 'bar-cn'
_myurl_bjs.host = 'athena.cn-north-1.amazonaws.com.cn'
_myurl_bjs.database = 'sample'
_myurl_bjs.query = {
    'connection': 'awsathena+jdbc://{aws_access_key_id}:{aws_secret_access_key}@athena.{region_name}.amazonaws.com.cn/{schema_name}'}

x = AthenaDialect()
_myopts = x.create_connect_args(_myurl)
print(_myopts)

_myopts = x.create_connect_args(_myurl_zhy)
print(_myopts)

_myopts = x.create_connect_args(_myurl_bjs)
print(_myopts)
