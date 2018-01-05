import os
from oauth2client import client, tools
from oauth2client.file import Storage


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'music-list'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'music-list.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    if not credentials:
        print ("Could not retrieve and/or store credentials")
    return credentials


def get_fileid_from_title(title):
    '''retrives id of file to download'''
    print("Document is \'{0}\'".format(title))
    return True

def download():
    ''' retrieve spreadsheet from google drive'''
    file_id = get_fileid_from_title("Music Favorites")
    print("Downloading...")
    return True


def edit():
    '''make changes to spreadsheet'''
    print("Editing...")
    return True


def upload():
    '''re-upload spreadsheet to google drive'''
    print("Updating...")
    return True


def main():
    credentials = get_credentials()
    if not credentials:
        return False

    if not download():
        return False
    if not edit():
        return False
    if not upload():
        return False
    print("Success!")
    return True


if __name__ == "__main__":
    main()
