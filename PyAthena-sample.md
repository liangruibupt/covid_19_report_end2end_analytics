## PyAthena
```bash
export YOUR_ACCESS_KEY_ID={YOUR_ACCESS_KEY_ID}
export YOUR_SECRET_ACCESS_KEY={YOUR_ACCESS_KEY_ID}
```
```python
from pyathena import connect
import os
from urllib.parse import quote_plus

YOUR_ACCESS_KEY_ID = os.environ['YOUR_ACCESS_KEY_ID']
YOUR_SECRET_ACCESS_KEY = os.environ['YOUR_SECRET_ACCESS_KEY']
print(YOUR_ACCESS_KEY_ID)
print(YOUR_SECRET_ACCESS_KEY)
cursor = connect(aws_access_key_id=quote_plus(YOUR_ACCESS_KEY_ID),
                 aws_secret_access_key=quote_plus(YOUR_SECRET_ACCESS_KEY),
                 s3_staging_dir='s3://covid-19-output-data/',
                 region_name='us-east-1').cursor()
cursor.execute("SELECT * FROM covid19.covid19_athena limit 10")
for row in cursor:
    print(row)
```

## SQLAlchemy
```python
from urllib.parse import quote_plus  # PY2: from urllib import quote_plus
from sqlalchemy.engine import create_engine
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import Table, MetaData
import os

YOUR_ACCESS_KEY_ID = os.environ['YOUR_ACCESS_KEY_ID']
YOUR_SECRET_ACCESS_KEY = os.environ['YOUR_SECRET_ACCESS_KEY']
print(YOUR_ACCESS_KEY_ID)
print(YOUR_SECRET_ACCESS_KEY)
conn_str = 'awsathena+rest://{aws_access_key_id}:{aws_secret_access_key}@athena.{region_name}.amazonaws.com:443/'\
           '{schema_name}?s3_staging_dir={s3_staging_dir}'
engine = create_engine(conn_str.format(
    aws_access_key_id=quote_plus(YOUR_ACCESS_KEY_ID),
    aws_secret_access_key=quote_plus(YOUR_SECRET_ACCESS_KEY),
    region_name='us-east-1',
    schema_name='covid19',
    s3_staging_dir=quote_plus('s3://covid-19-output-data/')))
many_rows = Table('covid19_athena', MetaData(bind=engine), autoload=True)
print(select([func.count('*')], from_obj=many_rows).scalar())
```