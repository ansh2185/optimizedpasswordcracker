import zipfile
import multiprocessing

# Move try_pwd outside so it can be pickled
def try_pwd(pwd, zip_path):
    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(pwd=bytes(pwd.strip(), 'utf-8'))
            return pwd
    except:
        return None

def crack_zip(zip_path, wordlist_path):
    with open(wordlist_path, 'r') as f:
        passwords = f.readlines()

    with multiprocessing.Pool(processes=4) as pool:
        results = pool.starmap(try_pwd, [(pwd, zip_path) for pwd in passwords])

    for pwd in results:
        if pwd:
            return pwd
    return None