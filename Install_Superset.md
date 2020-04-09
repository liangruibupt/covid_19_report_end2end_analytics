# Install Superset on AWS

- [Apache Superset official document](https://superset.apache.org/)
- [Apache Superset installation](https://superset.apache.org/installation.html)

## Start with Docker
```bash
# ssh to EC2 m5.xlarge or m5.2xlarge instance
sudo yum update -y

# install python3 gcc
sudo yum install -y python3 libpq-dev python3-dev
sudo yum install -y gcc gcc-c++

# add following into ~/.bashrc
echo "export PATH=/usr/local/bin:$PATH" >> ~/.bashrc
echo "alias python=python3" >> ~/.bashrc
echo "alias pip=pip3" >> ~/.bashrc
source ~/.bashrc
python --version

# install docker
sudo yum -y install docker
sudo usermod -a -G docker ec2-user
sudo systemctl start docker
sudo systemctl status docker
sudo systemctl enable docker
sudo chmod 666 /var/run/docker.sock
docker ps

# install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
docker-compose --version

# docker run superset
sudo yum install -y git curl
git clone https://github.com/apache/incubator-superset/
cd incubator-superset
# you can run this command everytime you need to start superset now:
docker-compose up

docker logs --follow <container-id>
docker-compose exec superset bash

# Access the web ui
ssh -i myKey.pem -L 8088:localhost:8088 ec2-user@EC2_IP
#ssh -L 8088:localhost:8088 -i ~/.ssh/ruiliang-lab-key-pair-us-east1.pem ec2-user@34.232.48.10
http://localhost:8088 or http://alb-dns/
login by admin:admin

# Superset can display maps using Mapbox. Get the API key of Mapbox and set it to MAPBOX_API_KEY.
add MAPBOX_API_KEY=mapboxapikey to ./docker/.env
add MAPBOX_API_KEY = get_env_variable("MAPBOX_API_KEY") to ./docker/pythonpath_dev/superset_config.py
```

## Quick Configuration
| database  | pypi package | SQLAlchemy URI prefix |
| :-------- | :-------- | :-------- | 
| Amazon Athena | pip install "PyAthenaJDBC>1.0.9" --upgrade --user | awsathena+jdbc:// |
| Amazon Athena | pip install "PyAthena>1.2.0" --upgrade --user | awsathena+rest:// |
| Amazon Redshift | pip install sqlalchemy-redshift --upgrade --user | redshift+psycopg2:// |
| PostgreSQL    | pip install psycopg2 OR pip install psycopg2-binary | postgresql+psycopg2:// |

```bash
# When you start from docker, add the connectors by add `jre` and `pip install in Dockerfile`
RUN apt-get update && apt-get install -y default-jre

RUN pip install "PyAthenaJDBC>1.0.9" \
    && pip install "PyAthena>1.2.0" \
    && pip install sqlalchemy-redshift \
    && pip install psycopg2

# Restart superset after installation
docker-compose build
docker-compose up
```

## AWS China region Athena connection URI handling
[Athena-Superset-China](Athena-Superset-China.md)

## Quick Tutorials
[Tutorials guide](https://superset.incubator.apache.org/admintutorial.html)

1. Configure the [example weather data](https://github.com/dylburger/noaa-ghcn-weather-data)
```bash
    # sample weather dataset
    git clone https://github.com/dylburger/noaa-ghcn-weather-data.git
    cd noaa-ghcn-weather-data
    curl -O ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/2015.csv.gz
    curl -O ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
    gunzip 2015.csv.gz
    wc -l 2015.csv
    cut -d, -f1 2015.csv | sort | uniq | wc -l

    # Install required software
    pip install virtualenv --user
    virtualenv venv --python=python3
    source venv/bin/activate
    pip install numpy scipy matplotlib ipython jupyter pandas sympy nose sqlalchemy psycopg2-binary boto3
    # pip install -r requirements.txt
    python
    >>> import platform
    >>> platform.architecture()
    ('64bit', 'ELF')

    # Setting up the PostgreSQL database
    # Check the DB_HOST, DB_PORT, DB_USER, DB_PASSWORD from docker-compose.yml and docker/.env
    psql -h localhost -p 5432 -U superset -d superset
    superset=# CREATE DATABASE weather;
    superset=# exit
    
    psql -h localhost -p 5432 -U superset -d weather
    weather=# create user weather_read_only with password 'pass';
    CREATE ROLE
    weather=# create schema weather;
    CREATE SCHEMA

    # Loading the data into PostgreSQL
    ssh -i myKey.pem -L 8888:localhost:8888 ec2-user@EC2_IP
    # ssh -i ~/.ssh/ruiliang-lab-key-pair-us-east1.pem -L 8888:localhost:8888 ec2-user@34.200.239.149
    jupyter notebook Ingest_Data_Into_PostgreSQL.ipynb --port 8888 --no-browser
    # Run the notebook to load the data

    weather=# \dt
            List of relations
    Schema |       Name       | Type  |  Owner
    --------+------------------+-------+----------
    public | station_metadata | table | superset
    public | weather_data     | table | superset
    public | weather_types    | table | superset
    (3 rows)
    

    # Denormalizing the data and metadata, creating database indexes, separating data for specific weather types as views
    # postgresql://superset:superset@localhost:5432/weather
    # postgresql+psycopg2://superset:superset@localhost:5432/weather
    Superset cannot perform database joins, and so require that any data we want to analyze at the same time be in a single table.

    weather=# CREATE TABLE weather_data_denormalized AS 
    SELECT wd.station_identifier, 
           wd.measurement_date, 
           wd.measurement_type, 
           wt.weather_description, 
           wd.measurement_flag, 
           sm.latitude, 
           sm.longitude, 
           sm.elevation 
    FROM weather_data wd 
    JOIN station_metadata sm 
        ON wd.station_identifier = sm.station_id 
    JOIN weather_types wt 
        ON wd.measurement_type = wt.weather_type;

    weather=# CREATE INDEX date_index ON weather_data_denormalized (measurement_date);

    weather=# SELECT COUNT(*) FROM weather_data_denormalized WHERE measurement_date = '2015-01-01';

    weather=# CREATE INDEX type_index ON weather_data_denormalized (measurement_type);

    weather=# CREATE INDEX description_index ON weather_data_denormalized (weather_description);

    weather=# CREATE INDEX flag_index ON weather_data_denormalized (measurement_flag);

    weather=# CREATE INDEX elevation_index ON weather_data_denormalized (elevation);

    weather=# CREATE VIEW precipitation_data AS SELECT * FROM weather_data_denormalized WHERE measurement_type = 'PRCP';

    weather=# SELECT COUNT(*) FROM precipitation_data;

    GRANT SELECT ON ALL TABLES IN SCHEMA public TO weather_read_only;

    weather=# \dt
                   List of relations
    Schema |           Name            | Type  |  Owner
    --------+---------------------------+-------+----------
    public | station_metadata          | table | superset
    public | weather_data              | table | superset
    public | weather_data_denormalized | table | superset
    public | weather_types             | table | superset
    (4 rows)

    deactivate
```

2. Connecting to a new database
```bash
    postgresql://superset:superset@db:5432/weather
```

3. Adding a new table for weather_data_denormalized

4. Exploring your data
- You can use simple phrases to apply these filters, like “5 years ago” consider the dataset is 2015.
- In Superset, a saved query is called a Slice. You can create the Slice and use Chart Type as “Distribution - Bar Chart”
- Creating a dashboard and add it to a dashboard

## Exploring data with Apache Superset
1. Enabling Upload a CSV Functionality

Find the `examples` database in Sources -> Databases, within `Edit Database` page, check `Allow Csv Upload` checkbox.

2. Loading the 2011 [sample flight data](https://raw.githubusercontent.com/apache-superset/examples-data/master/tutorial_flights.csv) into `tutorial_flights` Table in Sources -> Upload a CSV. 

Using the `Travel Date` in `Parse Dates` field. Leaving all the other options in their default settings.

3. Create Charts and Dashboard

- Table Charts
![flights-tutorial-table-chat](media/flights-tutorial-table-chat.png)
![flights-tutorial-table-chat-db](media/flights-tutorial-table-chat-db.png)

- Pivot Table
![flights-tutorial-Pivot-chat](media/flights-tutorial-Pivot-chat.png)
![flights-tutorial-Pivot-chat-db](media/flights-tutorial-Pivot-chat-db.png)

- Line Chart
![flights-tutorial-Line-chat](media/flights-tutorial-Line-chat.png)
![flights-tutorial-Line-chat-db](media/flights-tutorial-Line-chat-db.png)


## Resource
- [Running Superset with Postgresql DB, Redis Caching, Nginx Server and SSL certification](https://github.com/p10rahulm/superset)
- [getting-started-with-superset-airbnb-data-exploration-platform](https://gist.github.com/codspire/41dd399912fdafbefcd2f2eb76022363)
- [running a jupyter notebook](https://jupyter.readthedocs.io/en/latest/running.html#running)

## Configure GUI on Amazon Linux (optional)
[Install a GUI on Amazon Linux 2 EC2](https://aws.amazon.com/premiumsupport/knowledge-center/ec2-linux-2-install-gui/)
```bash
# Install MATE
sudo yum update -y
sudo amazon-linux-extras install -y mate-desktop1.x
sudo bash -c 'echo PREFERRED=/usr/bin/mate-session > /etc/sysconfig/desktop'

# Install TigerVNC
sudo yum install -y tigervnc-server
vncpasswd   # Passw0rd
## vncserver :1
sudo cp /lib/systemd/system/vncserver@.service /etc/systemd/system/vncserver@.service
sudo sed -i 's/<USER>/ec2-user/' /etc/systemd/system/vncserver@.service
sudo systemctl daemon-reload
sudo systemctl enable vncserver@:1
sudo systemctl start vncserver@:1
sudo systemctl status vncserver@:1

# Connect to the GUI using the VNC
ssh -L 5901:localhost:5901 -i PEM_FILE ec2-user@INSTANCE_IP
#ssh -L 5901:localhost:5901 -i ~/.ssh/ruiliang-lab-key-pair-us-east1.pem ec2-user@34.200.239.149
#vnc://34.200.239.149 on safari

# Install Web Browsers
sudo amazon-linux-extras install -y epel
sudo yum install -y chromium
```