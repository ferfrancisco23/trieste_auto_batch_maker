import os
import winreg

class TriesteAccountMethods:

    def check_environ(self):
        if "TRIESTE_USERNAME" and "TRIESTE_PASSWORD" in os.environ:
            return True
        else:
            return False

    def add_edit_account(self):
        # take trieste username and password from user
        trieste_username = input("Trieste Username: ")
        trieste_password = input("Trieste Password: ")
        linkdev_name = input("Enter your name EXACTLY as it appears on drop down boxes in Trieste: ")

        new_environ_variable = {"TRIESTE_USERNAME": trieste_username,
                                "TRIESTE_PASSWORD": trieste_password,
                                "LINKDEV_NAME": linkdev_name}

        for name, value in new_environ_variable.items():
            # Specify the key path to add the environment variable
            key_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'

            # Open the key for writing
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)

            # Add the new environment variable to the key
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)

        winreg.CloseKey(key)

        os.environ["TRIESTE_USERNAME"] = trieste_username
        os.environ["TRIESTE_PASSWORD"] = trieste_password