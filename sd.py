import re
from subprocess import call
from pathlib import Path

def choose_option():
    print(f"\nWelcome to systemd service maker!")
    print(f"What would you like to do?")
    print(f"\n1) New service")
    print(f"2) List services")
    print(f"3) Delete service\n")
    choice = input(":")
    while not re.fullmatch(r'\d',choice):
        print(f"\nNot a valid option. Please choose 1, 2, or 3!")
        choice = input("\nTry again:")
        return int(choice)
    else:
        return int(choice)

class ServiceMaker:
    """program that makes simple systemd services."""

    def __init__(self, choice, service_name=''):
        """Select from: new, list, delete and write the name of the service"""
        self.choice = choice
        self.service_name = service_name

    def new_service(self):
        """Makes new service"""


        #Enter the description for your unit file
        print(f"\nEnter a description for your service")
        description = input(":")

        #Specify where your bash script or other script is located
        print(f"\nWhere is your script or program located?")
        print(f"\n1) /usr/local/bin/")
        print(f"2) /usr/sbin/")
        print(f"3) other location")
        try:
            path_option = int(input("\n:"))
        except ValueError:
            print(f"\nNot a valid option. Please choose 1, 2, or 3!")
            path_option = int(input("\nTry again:"))

        if path_option == 1:
            path_directory = "/usr/local/bin/"

        if path_option == 2:
            path_directory = "/usr/sbin/"

        #User provides his own directory to the script
        if path_option == 3:
            print(f"\nEnter the path location to your script or program")
            path_directory = input(":")
            while not re.fullmatch(r'/\D{3,26}/\D{3,26}/',path_directory):
                print(f"\nPlease type a correct directory")
                print(f"\n'{path_directory}' is not a valid directory")
                print(f"Must be in this format: '/path/to/script/'")
                path_directory = input(f"\nTry again:")
            else:
                None

        print(f"\nWhat is the name of your script? e.g. restic.sh")
        script_name = input(":")

        execute_script = call(["sudo","chmod", "+x", f"{path_directory}{script_name}"])

        service = "[Unit]\n"
        service += f"{description}\n"
        service += "\n"
        service += "[Service]\n"
        service += f"ExecStart={path_directory}{script_name}\n"
        service += "\n"
        service += "[Install]\n"
        service += "WantedBy=multi-user.target"

        #Asking the user where to save the .service unit file
        print(f"\nWhere do you want to save your .service file?")
        print(f"\n1) /etc/systemd/system/")
        print(f"2) other location")
        service_option = input("\n:")
        if not service_option == int(1) or int(2):
            print(f"\nNot a valid option. Please choose 1, or 2!")
            service_option = int(input("\nTry again:"))
        else:
            None

        if int(service_option) == 1:
            service_location = "/etc/systemd/system/"
        elif int(service_option) == 2:
            print(f"Enter location of .service file")
            service_location = input(f"\n:")
        else:
            None
            
        
        service_path = Path(service_location)

choice = choose_option()
systemd_action = ServiceMaker(choice)

if choice == 1:
    systemd_action.new_service()

else: 
    None
