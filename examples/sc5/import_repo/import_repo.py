#!/usr/bin/env python
from securitycenter import SecurityCenter5


class ExtendedSecurityCenter(SecurityCenter5):
    def import_repo(self, repo_id, fileobj):
        '''
        Imports a repository package using the repository ID specified.
        '''
        # Step 1, lets upload the file
        filename = self.upload(fileobj).json()['response']['filename']

        # Step 2, lets tell SecurityCenter what to do with the file
        return self.post('repository/{}/import'.format(repo_id), json={'file': filename})


if __name__ == '__main__':
    from getpass import getpass
    
    # Lets get all of the information needed
    hostname = raw_input('SC Address : ')
    username = raw_input('Username   : ')
    password = getpass('Password   : ')
    filename = raw_input('Repository File : ')
    repo_id = raw_input('Repository ID : ')

    # Logging into SecurityCenter
    sc = ExtendedSecurityCenter(hostname)
    sc.login(username, password)

    # Uploading the Repository
    with open(filename, 'rb') as fileobj:
        sc.import_repo(sc, repo_id, fileobj)