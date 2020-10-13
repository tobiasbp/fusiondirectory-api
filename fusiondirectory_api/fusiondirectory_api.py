import re
import requests

class FusionDirectoryAPI():

    def __init__(self, host, user, password, database):

        # The session to use for all requests
        self._session = requests.Session()
    
        # The URL of the FD server
        self._url = f'{host}/jsonrpc.php'

        # Log in to get this ID from FD
        self._session_id = None
        
        # Send this ID wuth all requests
        self._id = "API"

        # Login to FD (Get a session_id)
        self.login(user, password, database)


    def login(self, user, password, database):
        """
        Login to FD by getting a session ID to include in post
        """
        data = {
            "method": "login",
            "params": [database, user, password]
            }
        self._session_id = self._post(data)


    def is_user_locked(self, user_dn):
        """
        Returns an associative array of booleans, the keys are the
        dns of the users. 0 = unlocked, 1 = locked.
        """
        data = {
            "method": "isUserLocked",
            "params": [self._session_id, user_dn]
            }
        return self._post(data)

    def list_types(self):
        """
        List of object types
        """
        data = {
            "method": "listTypes",
            "params": [self._session_id]
            }
        return self._post(data)

    def get_base(self):
        """
        Return he configured LDAP base for the selected LDAP
        in this webservice session (see login)
        """
        data = {
            "method": "getBase",
            "params": [self._session_id]
            }
        return self._post(data)

    def get_id(self):
        """
        Get current session ID
        """
        data = {
            "method": "getId",
            "params": [self._session_id]
            }
        return self._post(data)


    def list_ldaps(self):
        """
        List LDAP servers managed by FD
        """
        data = {
            "method": "listLdaps",
            "params": []
            }
        return self._post(data)


    def lock_user(self, user_dn):
        """
        Lock a user
        """
        data = {
            "method": "lockUser",
            "params": [self._session_id, user_dn, "lock"]
            }
        self._post(data)
        return True

    def unlock_user(self, user_dn):
        """
        Unlock a user
        """
        data = {
            "method": "lockUser",
            "params": [self._session_id, user_dn, "unlock"]
            }
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

        if r['error'] == None:
            return r["result"]
        else:
            raise Exception("FD returned error: {r['error']}")
