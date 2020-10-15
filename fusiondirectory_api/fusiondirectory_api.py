import re
import requests


class FusionDirectoryAPI:
    def __init__(self, host, user, password, database, login=True):

        # The session to use for all requests
        self._session = requests.Session()

        # The URL of the FD server
        self._url = f"{host}/jsonrpc.php"

        # Log in to get this ID from FD
        self._session_id = None

        # Send this ID wuth all requests
        self._id = "API"

        # Login to FD (Get a session_id)
        if login:
            self.login(user, password, database)

    def delete(self, object_type, dn):
        """
        Delete an object

        Args:
            object_type (str): The type of the object to remove
            dn (str): The DN of the object to remove

        Returns:
            True on success
        """
        data = {"method": "delete", "params": [self._session_id, object_type, dn]}
        r = self._post(data)
        # Api returns nothing on success, so anything is an error
        if r:
            raise Exception(r)
        else:
            return dn

    def get_base(self):
        """
        Return the configured LDAP base for the selected LDAP
        in this webservice session (see login)
        """
        data = {"method": "getBase", "params": [self._session_id]}
        return self._post(data)

    def get_fields(self, object_type, dn=None, tab=None):
        """
        \brief Get all internal FD fields from an object (or an object type)
        *
        * Fields as they are stored in FusionDirectory
        *
        * \param string  $type the object type
        * \param string  $dn   the object to load values from if any
        * \param string  $tab  the tab to show if not the main one
        *
        * \return All FD attributes organized as sections
        """
        data = {
            "method": "getFields",
            "params": [self._session_id, object_type, dn, tab],
        }
        return self._post(data)

    def count(self, object_type, ou=None, filter=""):
        """
        Get the number of an object type in an ou

        Args:
            object_type (str): The object type
            ou (str): The OU to search for objects in. Base is used if OU is None
            filter (str): An LDAP filter to limit the results

        Returns:
            The number of objects of type object_type in the OU (int)
        """
        # Querying for these object types will return an error.
        # Return a count of 0 instead (There may be others)
        if object_type.upper() in ["DASHBOARD", "SPECIAL", "LDAPMANAGER"]:
            return 0
        data = {
            "method": "count",
            "params": [self._session_id, object_type, ou, filter],
        }
        return self._post(data)

    def get_id(self):
        """
        Get current session ID

        Returns:
            The currents session id (str)
        """
        data = {"method": "getId", "params": [self._session_id]}
        return self._post(data)

    def list_objects(self, object_type, attributes=None, ou=None, filter=""):
        """
        Get list of objects. Potentially with LDAP attributes.

        Arguments:
            object_type (str): The object type to list
            attributes: The attributes to fetch.
            If this is a single value, the resulting dictionary will have
            for each dn the value of this attribute.
            If this is an array, the keys must be the wanted attributes,
            and the values can be either 1, '*', 'b64' or 'raw'
            depending if you want a single value or an array of values.
            Other values are considered to be 1.
            'raw' means untouched LDAP value and is only useful for dns.
            'b64' means an array of base64 encoded values and is mainly useful for binary attributes.
            ou (str): The LDAP branch to search in, base will be used if it is None
            filter (str): An additional filter to use in the LDAP search.

        Returns:
            A list of objects as a dictionary with DN as keys (list)
        """
        data = {
            "method": "ls",
            "params": [self._session_id, object_type, attributes, ou, filter],
        }
        return self._post(data)

    def list_ldaps(self):
        """
        List LDAP databases/servers managed by FD. These are the valid
        values for the 'database' argument in login()

        Returns:
            A list of databases managed by FusionDirectory
        """
        data = {"method": "listLdaps", "params": []}
        return self._post(data)

    def list_types(self):
        """
        List of object types known to the server

        Returns:
            A dictionary with object type as key and
            object name as value (dict)
        """
        data = {"method": "listTypes", "params": [self._session_id]}
        return self._post(data)

    def list_tabs(self, object_type, dn=None):
        """
        Get tabs for on an object type. If a DN is supplied
        the data returned will show if the tab is active for the
        for the object with the DN.

        Args:
            object_type (str): The object type to get tabs for
            dn (str): The dn of an object to get active values from

        Returns:
            A dictionary with tabs as keys and a dictionary with
            tab name (str) and active (Bool)
        """
        data = {"method": "listTabs", "params": [self._session_id, object_type, dn]}
        return self._post(data)

    def info(self, object_type):
        """
        Get the information on an object type

        Args:
            object_type: The type of object to get information for

        Returns:
            A dictionary of information on the object type
        """
        data = {"method": "infos", "params": [self._session_id, object_type]}
        return self._post(data)

    def is_user_locked(self, user_dn):
        """
        Get the lock state of one, or more, users

        Args:
            user_dn (str/list): A single DN or a list of DNs

        Returns:
            result: A dictionary with user DNs as keys and the
            lock state as values: 0 = unlocked, 1 = locked
        """
        data = {"method": "isUserLocked", "params": [self._session_id, user_dn]}
        return self._post(data)

    def lock_user(self, user_dn):
        """
        Lock a user

        Args:
            user_dn (str): The DN of the user to lock

        Returns:
            Bool: True on success
        """
        data = {"method": "lockUser", "params": [self._session_id, user_dn, "lock"]}
        self._post(data)
        return True

    def login(self, user, password, database):
        """
        Login to FD by getting a session ID to include in posts

        Args:
            user (str): The username to login as
            password (str): The password of the user
            database (str): The name of the LDAP database/server to use

        Returns:
            Session id (str)
        """
        data = {"method": "login", "params": [database, user, password]}
        self._session_id = self._post(data)
        return self._session_id

    def logout(self):
        """
        Log out of FusionDirectory. Deletes session ID

        Returns:
            Bool: True
        """
        data = {"method": "logout", "params": [self._session_id]}
        r = self._post(data)
        self._session_id = None
        return r

    def get_recovery_token(self, email):
        """
        Generate a password recovery token for a user

        Args:
            email (str): An email address associated with a user

        Returns:
            A recovery token (str)
        """
        data = {"method": "recoveryGenToken", "params": [self._session_id, email]}
        r = self._post(data)
        return r["token"]

    def get_template(self, object_type, dn):
        """
        Get template

        Args:
            object_type (str): The type of the object the template is for
            dn (str): The DN of the template

        Returns:
            dict: FusionDirectory attributes organized as tabs
        """
        data = {"method": "gettemplate", "params": [self._session_id, object_type, dn]}
        return self._post(data)

    def delete_tab(self, object_type, dn, tab):
        """
        Deletes a tab, with fields, from an object

        Args:
            object_type (str): The type of the object to remove a tab from
            dn (str): The dn of the object to remove a tab from
            tab (str): The tab to remove

        Returns:
            The object DN on success
        """
        data = {
            "method": "removetab",
            "params": [self._session_id, object_type, dn, tab],
        }
        return self._post(data)

    def set_fields(self, object_type, dn, values):
        """
        Add/Update values in an object

        Args:
            object_type (str): The type of the object to update
            dn (str): The dn of the object to update
            values (str): A dictionary of values to update the object with.
            First level keys are tabs, second level keys should be the same
            keys returned by get_fields (without section, directly the attributes).

        Returns:
            The object DN on success
        """
        data = {
            "method": "setFields",
            "params": [self._session_id, object_type, dn, values],
        }
        return self._post(data)

    def set_password(self, uid, password, token):
        """
        Set the password of a user

        Args:
            uid (str): UID of the user to change password for
            password (str): The new password for the user
            token (str): a token generated by a get_recovery_token()

        Returns:
            True on success
        """
        data = {
            "method": "recoveryConfirmPasswordChange",
            "params": [self._session_id, uid, password, password, token],
        }
        return self._post(data)

    def unlock_user(self, user_dn):
        """
        Unlock a user

        Args:
            user_dn (str): The DN of the user to unlock

        Returns:
            result: True on success
        """
        data = {"method": "lockUser", "params": [self._session_id, user_dn, "unlock"]}
        self._post(data)
        return True

    def use_template(self, object_type, dn, values):
        """
        Create an object from a template

        Args:
            object_type (str): The type of the object to create
            dn (str): The dn of the template to use
            values (str): A dictionary of values for the fields in the new object.
            First level keys are tabs, second level keys should be the same
            keys returned by get_fields (without section, directly the attributes).

        Returns:
            The object DN of the new object on success
        """
        data = {
            "method": "usetemplate",
            "params": [self._session_id, object_type, dn, values],
        }
        r = self._post(data)
        return r

    def _post(self, data):
        """
        Send data to the FusionDirectory server

        Args:
            data: The data to post

        Returns:
            result: The value of the key 'result' in the JSON returned by the server
        """
        # All requests must have this, non session, ID (Don't know why?)
        data["id"] = self._id

        # Post
        r = self._session.post(self._url, json=data)

        # Raise exception on error codes
        r.raise_for_status()

        # Get the json in the response
        r = r.json()

        if r["error"]:
            raise Exception(f"FD returned error: {r['error']}")
        else:
            # The result value can have the key errors with a list
            if type(r["result"]) == dict and r["result"].get("errors"):
                raise Exception("".join(r["result"]["errors"]))
            else:
                return r["result"]
