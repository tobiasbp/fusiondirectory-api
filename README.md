# fusiondirectory-api
A Python3 wrapper for the RPC API of LDAP manager [FusionDirectory}(https://fusiondirectory-user-manual.readthedocs.io/en/latest/).
You need to enable the plugin _webservice_ in FusionDirectory to be able to use the API.

This wrapper supports the RPC based API in versions of FusionDirectory 1.3. This API may be deprecated in version 1.4
as a change to a REST based API is planned.

# Installation

Install with pip: `pip3 install fusiondirectory-api"

# Overview
A description of key concepts when working with the FusionDirectory API

## Databases
FusionDirectory can handle more than a single database. In the GUI, the database to use can be selcted from a drop down.
When the using the API, the name of the database to use, must be supplied when logging in.

## Objects
FusionDirectory handles a number of _objects_.
In general, the object type needs to be specified along with the _object_'s [DN](https://docs.microsoft.com/en-us/previous-versions/windows/desktop/ldap/distinguished-names)
when manipulating objects with the API.

The object types supported by an installation of FusionDirectory, depends on which plugins are enabled. The list of objects
in an installation can be retrieved by calling _list_types()_.

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
The tabs available for an object type can be retrieved by calling _list_tabs(OBJECT_TYPE)_. By default, tabs are inactive.
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

# Examples
This section contains som examples showing how to use the API.

## Logging in
Log in, and show available object types.
```
from fusiondirectory_api import FusionDirectoryAPI

api = FusionDirectoryAPI(
  host = "https://ldap.example.org",
  user = "user-name",
  password = "secret-password",
  database = "my-ldap",
  )

object_types = api.list_types()
print(object_types)

```

## Creating a new user
Let's create a new object of type __USER__.
Its assumed you have created the object _api_ as shown in the exampel above.
Note, that the password is a list, because the inner workings are based on the GUI, where
the user has to type password twice (To confirm).

```
# The data for the new user
values = {
  "user": {
    "uid": "bj",
    "sn": "Jacobsen",
    "givenName": "Bent",
    "userPassword": ["", "CzehlFp5WBLLULcCbuGOGrhy13fPajIL", "CzehlFp5WBLLULcCbuGOGrhy13fPajIL"],
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

# Methods 
The methods in the API. For now look in the code. All methods have doc strings.
