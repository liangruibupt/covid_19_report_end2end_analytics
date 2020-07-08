# Apache Superset LDAP authentication with Active Directory

Check the superset support issue: https://github.com/apache/incubator-superset/issues/3221 and support feature https://github.com/apache/incubator-superset/issues/4840

Superset leverage the Flask-AppBuilder to do the Active Directory integration

## Modify the superset/config.py

```
# AUTH_LDAP
from flask_appbuilder.security.manager import AUTH_DB,AUTH_LDAP

# LDAP Setting
AUTH_TYPE = AUTH_LDAP

# Uncomment to setup Full admin role name
AUTH_ROLE_ADMIN = 'admin'

# Uncomment to setup Public role name, no authentication needed
#AUTH_ROLE_PUBLIC = 'Public'

# Will allow user self registration
AUTH_USER_REGISTRATION = True

# The default user self registration role as admin
AUTH_USER_REGISTRATION_ROLE = "admin"

# When using LDAP Auth, setup the ldap server
AUTH_LDAP_SERVER = "ldap://ldap.xx/"
AUTH_LDAP_SEARCH = "ou=People,dc=ldap,dc=xx"
AUTH_LDAP_UID_FIELD = "cn"
#AUTH_LDAP_UID_FIELD = "sAMAccountName"
#AUTH_LDAP_APPEND_DOMAIN = '**'

#The user used to connect the LDAP
AUTH_LDAP_BIND_USER = "cn=superset,ou=app,dc=ldap,dc=xx"
AUTH_LDAP_BIND_PASSWORD = "********"
```
