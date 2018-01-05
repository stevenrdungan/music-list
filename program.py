

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
