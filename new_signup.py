import os
import sys
import platform

def get_user_documents_path():
    try:
        if platform.system() == "Windows":
            return os.path.join(os.path.expanduser("~"), "Documents")
        else:
            return os.path.join(os.path.expanduser("~"), "Documents")
    except:
        return os.path.abspath(".")
