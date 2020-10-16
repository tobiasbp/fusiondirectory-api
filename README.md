# Introduction
_fusiondirectory-api_ is a Python3 wrapper for the RPC API of LDAP manager [FusionDirectory](https://fusiondirectory-user-manual.readthedocs.io/en/latest/).
You need to enable the plugin _webservice_ in FusionDirectory to be able to use the API.

This wrapper supports the RPC based API in versions of FusionDirectory up to 1.3. This API may be deprecated in version 1.4
as a change to a REST based API is planned.

As FusionDirectory manages data in LDAP, the database can also be updated directly in LDAP. The API, however,
allows for restriction of acces using FusionDirectory's Access Control Lists, and the ability to create
objects based on templates defined in the GUI. It may also be of advantage to you, that you can access the data
in LDAP via HTTP/HTTPS on ports 80/443 instead of through the LDAP ports 389/636.

# Installation

Install with pip: `pip3 install fusiondirectory-api`

# Overview
A description of key concepts when working with the FusionDirectory API

## Databases
FusionDirectory can handle more than a single database. In the GUI, the database to use can be selcted from a drop down.
When the using the API, the name of the database to use, must be supplied when logging in.

## Objects
FusionDirectory organizes data in _objects_. There are different types of _object_. One type of object is _USER_.
In general, the object type needs to be specified along with the _object_'s [DN](https://docs.microsoft.com/en-us/previous-versions/windows/desktop/ldap/distinguished-names)
when manipulating objects with the API.

The object types supported by an installation of FusionDirectory, depends on which plugins are enabled. The list of objects
in an installation can be retrieved by calling _get_object_types()_.

These are the objects in the FusionDirectory installation of the author of this project:
* CONFIGURATION
* OGROUP
* PRINTER
* ROLE
* WORKSTATION
* SAMBADOMAIN
* USER
* TERMINAL
* SERVER
* MOBILEPHONE
* COUNTRY
* ACLASSIGNMENT
* ACLROLE
* COMPONENT
* GROUP
* DCOBJECT
* DEPARTMENT
* DOMAIN
* LOCALITY
* ORGANIZATION
* PHONE

## Tabs
The data for an _object_, is organized in _tabs_. The tabs available for an object type, depends on the activated plugins.
The tabs available for an object type can be retrieved by calling _get_tabs(OBJECT_TYPE)_. By default, tabs are inactive.
The following dictionary shows the avaiable tabs for the object type _USER_ in the author's installation.
The outher keys are the values which should be used when refering to a tab when using the API. The _name_ is the name
for the tab in the webinterface GUI.

```
{
  'user': {'name': 'User', 'active': True},
  'posixAccount': {'name': 'Unix', 'active': False},
  'personalInfo': {'name': 'Personal', 'active': False},
  'mailAccount': {'name': 'Mail', 'active': False},
  'sambaAccount': {'name': 'Samba', 'active': False},
  'userRoles': {'name': 'Groups and roles', 'active': False},
  'sshAccount': {'name': 'SSH', 'active': False},
  'userCertificates': {'name': 'Certificates', 'active': False},
  'reference': {'name': 'References', 'active': True},
  'ldapDump': {'name': 'LDAP', 'active': True}
}
```
## Templates
Objects can be created from templates. The templates can not be created from the API. They need to be created manually in the GUI.
The DN of the template is needed when creating an object from a template.

# Examples
This section contains som examples showing how to use the API.

## Logging in
Log in, and show available object types.
```
# Import the library
from fusiondirectory_api import FusionDirectoryAPI

# Log in to the FusionDirectory server
api = FusionDirectoryAPI(
  host = "https://ldap.example.org",
  user = "user-name",
  password = "secret-password",
  database = "my-ldap",
  )

# Get the object types available
object_types = api.get_object_types()

# Print the object types
print(object_types)

```

## Creating a new user
Let's create a new object of type __USER__.
Its assumed you have created the object _api_ as shown in the example above.
Note, that the password is a list, because the inner workings are based on the GUI, where
the user has to type the password twice (To confirm). The 1st entry in the list should
be the empty string, the 2nd and 3rd entries must be the password to be used. That is
the 2nd and 3rd entry must be identical.

```
# The data for the new user
values = {
  "user": {
    "uid": "bj",
    "sn": "Jacobsen",
    "givenName": "Bent",
    "userPassword": ["", "secretpassword", "secretpassword"],
  }
}

# Create the new user
new_user_dn = api.create_object("USER", values)

# Print the DN of the new user
print(f"Created new user: {new_user_dn}")
```

## Updating a user
Add an email address to the user we created above.

```
# The data to add to the user
values = {
  "mailAccount": {
    "mail": "bj@example.org"
  }
}

# Update the user
updated_user_dn = api.update_object("USER", new_user_dn, values)

# Print to confirm the change
print(f"Updated data for user: {updated_user_dn}")
```

## Deleting a user
Delete the user from the examples above.

```
# Delete the user
deleted_user_dn = api.delete_object("USER", new_user_dn)

# Print to confirm
print(f"Deleted user: {deleted_user_dn}")
```

# Class documentation
Technical documentation. For a description of each medthod, look at doc strings in source code.

## Constructor
* FusionDirectoryAPI(host, user, password, database, login=True)

## Methods
* create_object_from_template(object_type, template_dn, values)
* create_object(object_type, values)
* delete_tab(object_type, dn, tab)
* delete_object(object_type, dn)
* get_base()
* get_fields(object_type, dn=None, tab=None)
* get_number_of_objects(object_type, ou=None, filter="")
* get_id()
* get_objects(object_type, attributes=None, ou=None, filter="")
* get_databases()
* get_object_types()
* get_tabs(object_type, dn=None)
* get_info(object_type)
* get_recovery_token(email)
* get_template(object_type, dn)
* is_user_locked(user_dn)
* lock_user(user_dn)
* login(user, password, database)
* logout()
* set_password(uid, password, token)
* unlock_user(user_dn)
* update_object(object_type, dn, values)
