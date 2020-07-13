try:
    import os
    import json
except ImportError as e: # most likely a ModuleNotFoundError
    raise Exception(f'Could not import a module: {e}.')

class User:
    '''
    User class to handle song performance storing.

    Args:
        path       (str) : indicates location of JSON user file
    Returns:
        self.data (dict) : all user and song data
    '''
    def __init__(self):
        self.data = None # Upon initializing create an empty dict
        self.path = None
        return

    def _load_data(self):
        with open(self.path, 'r') as file:
            self.data = json.load(file)
        return

    def validate(self, username, password):
        if not username or not password:
            return 'Both fields must be filled in.'
        directory = [[files,root] for root, dirs, files in os.walk('.\\assets\\users\\')]
        if len(directory) == 1 and not directory[0][0]:
            return 'User does not exist.'
        else:
            for file in directory[0][0]:
                if username in file:
                    self.path = directory[0][1]+file
                    self._load_data()
                    if password == self.data['password']:
                        self.username = username
                        return
                    else:
                        self.path = None
                        self.data = {}
                        return 'Invalid password.'
            return 'User does not exist.'

    def create(self, username, password):
        if not username or not password:
            return 'Both fields must be filled in.'
        error = self.validate(username,password)
        if error == 'User does not exist.':
            self.path = f'.\\assets\\users\\{username}.json'
            self.username = username
            self.save({'password':password})
            return
        else:
            return 'User already exists.'

    def remove(self):
        os.remove(self.path)
        return

    def save(self,data):
        self.data = data
        with open(self.path, 'w') as file:
            json.dump(data, file, indent=4)
        return

    def get_data(self):
        if self.path:
            self._load_data()
            return self.data
        else:
            return None

    def get_username(self):
        if self.path:
            return self.username
        else:
            return None
