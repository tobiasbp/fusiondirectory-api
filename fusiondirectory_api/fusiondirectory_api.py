import re
import requests


class FusionDirectoryAPI:
    def __init__(self, host, user, password, database):

        # The session to use for all requests
        self._session = requests.Session()

        # The URL of the FD server
        self._url = f"{host}/jsonrpc.php"

        # Log in to get this ID from FD
        self._session_id = None

        # Send this ID wuth all requests
        self._id = "API"

        # Login to FD (Get a session_id)
        self.login(user, password, database)

    def get_base(self):
        """
        Return the configured LDAP base for the selected LDAP
        in this webservice session (see login)
        """
        data = {"method": "getBase", "params": [self._session_id]}
        return self._post(data)

    def count(self, object_type, ou=None, filter=""):
        """
        Return the number of objects of type $type in $ou
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
        """
        data = {"method": "getId", "params": [self._session_id]}
        return self._post(data)

    def list(self, object_type, attributes=None, ou=None, filter=""):
        """
        Get list of objects of type object_type in ou
        object_type: The objectType to list
        attributes: The attributes to fetch.
        If this is a single value, the resulting associative array will have for each dn the value of this attribute.
        If this is an array, the keys must be the wanted attributes, and the values can be either 1, '*', 'b64' or 'raw'
        depending if you want a single value or an array of values.
        Other values are considered to be 1.
        'raw' means untouched LDAP value and is only useful for dns.
        'b64' means an array of base64 encoded values and is mainly useful for binary attributes.
        ou: The LDAP branch to search in, base will be used if it is None
        filter: An additional filter to use in the LDAP search.
        Returns a list of objects as a dictionary (keys are dns)
        """
        data = {
            "method": "ls",
            "params": [self._session_id, object_type, attributes, ou, filter],
        }
        return self._post(data)

    def list_ldaps(self):
        """
        List LDAP servers managed by FD
        """
        data = {"method": "listLdaps", "params": []}
        return self._post(data)

    def list_types(self):
        """
        List of object types know to the server
        """
        data = {"method": "listTypes", "params": [self._session_id]}
        return self._post(data)

    def info(self, object_type):
        """
        The information on this object type as an associative array
        """
        data = {"method": "infos", "params": [self._session_id, object_type]}
        return self._post(data)

    def is_user_locked(self, user_dn):
        """
        Returns an associative array of booleans, the keys are the
        dns of the users. 0 = unlocked, 1 = locked.
        """
        data = {"method": "isUserLocked", "params": [self._session_id, user_dn]}
        return self._post(data)

    def lock_user(self, user_dn):
        """
        Lock a user
        """
        data = {"method": "lockUser", "params": [self._session_id, user_dn, "lock"]}
        self._post(data)
        return True

    def login(self, user, password, database):
        """
        Login to FD by getting a session ID to include in post
        """
        data = {"method": "login", "params": [database, user, password]}
        self._session_id = self._post(data)

    def unlock_user(self, user_dn):
        """
        Unlock a user
        """
        data = {"method": "lockUser", "params": [self._session_id, user_dn, "unlock"]}
        self._post(data)
        return True

    def _post(self, data):
        """
        Args:
          data: The data to post
        """
        # All requests must have this, non session, ID (Don't know why?)
        data["id"] = self._id

        # Post
        r = self._session.post(self._url, json=data)

        # Raise exception on error codes
        r.raise_for_status()

        # Sometimes there is no content (LockUser)
        if not r.content:
            print(f"No content for : {data}")
            return r

        # Get the json in the result
        r = r.json()

        if r["error"] == None:
            return r["result"]
        else:
            print(r)
            raise Exception(f"FD returned error: {r['error']}")
