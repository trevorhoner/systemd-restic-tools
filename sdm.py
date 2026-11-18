import re
import json
from subprocess import call
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(prog='sdm', usage='%(prog)s [options]', description='systemd manager', epilog='Provides a fast way to efficiently manage and create systemd files')
parser.add_argument('-n', '--new', action='store_true', help='makes new unit file')
parser.add_argument('-l', '--list', action='store_true', help='list all created unit files')
parser.add_argument('-d', '--delete', nargs='?', const='delete', default=None, help='deletes a unit file')

class ServiceMaker:
    """program that makes simple systemd services."""

    def __init__(self):
        """Select from: new, list, delete and write the name of the service"""
        #self.choice = choice
        #self.service_name = service_name
        self.data_path = Path("./data.json")

    def new_service(self):
        """Makes new service"""
        #Make a name for your new service
        print(f"\nMake a name for your new service")
        service_name = input(":")
        self.new_service = f"{service_name}.service"

        #Checks if there's a pre-existing service with the same name
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            for line in json_data:
                if re.search(self.new_service, line):
                    print(f"\n'{self.new_service}' is already a service! What would you like to do?")
                    choice = input(f"(o)verwrite or (n)ew file?: ")

                    if choice == "o":
                        print(f"\nOverwiting old service.")
                        return None

                    else:
                        print(f"\nMake a new name for your new service")
                        service_name = input(":")
                        self.new_service = f"{service_name}.service"

    def service_information(self):
        """Enter the description for your unit file"""

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
        print(f"\n1) ~/sdm/services/")
        print(f"2) other location")
        service_option = int(input("\n:"))

        try:
            while service_option not in (1,2):
                print(f"Please pick 1 or 2.")
                service_option = int(input("\nTry again: "))
        except ValueError:
            print(f"Please pick 1 or 2")

        if service_option == 1:
            service_location = "./services/"
        elif service_option == 2:
            print(f"Enter directory of .service file")
            service_location = input(f"\n:")
        else:
            None
            
        
        self.service_path = Path(f"{service_location}{self.new_service}")
        self.data = f"{self.new_service}           Path: {self.service_path}"

        self.service_path.parent.mkdir(parents=True, exist_ok=True)
        self.service_path.write_text(service)

    def activate_service(self):
        """Activates new unit file"""

        print(f"\nDo you wish to start and enable {self.new_service}?")
        choice = input("y/n: ")

        if choice == "y":
            call(["sudo", "systemctl", "link", self.service_path])
            call(["sudo", "systemctl", "daemon-reload"])
            call(["sudo", "systemctl", "start", self.new_service])

        else:
            return None

    def write_service(self):
        """Write service to JSON file with directory"""

        json_data = []

        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

        else:
            json_data = []

        json_data.append(self.data)

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    def list_services(self):
        """Lists services from data.json"""

        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            for service in json_data:
                print(f"\n{service}")
        else:
            print("\nThere are no services!")
        
    def delete_service(self):
        """deletes service from list"""

        #If no service is passed as an argument, you delete from a list
        if args.delete == "delete":
            if self.data_path.exists():

                with open(self.data_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                count = 1
                for service in json_data:
                    print(f"\n[{count}] {service}")
                    count += 1

                print("\nWhich service do you want to delete?")
                self.choice = int(input("Enter a number: "))

                while self.choice not in range(count):
                    print("\nThat's not a valid number from the list. Try again.")
                    self.choice = int(input("Enter a number: "))

                #The name and path of the service to be deleted
                delete_path = Path(re.search('(?<=Path: )\\D+',json_data[self.choice-1])[0])
                service_name = re.search('(?:.{3,20}).service',json_data[self.choice-1])[0]
                
                print(f"\nAre you sure you want to delete {service_name}?")
                self.fail_choice = input(f"y/n: ")

                if self.fail_choice == "y":
                    call("sudo","rm","-r",{delete_path})

                elif self.fail_choice == "n":
                    return None

                else:
                    print("\nNot a valid choice.")
                    print("Please enter (y)es or (n)o")
                    self.fail_choice = input(f"y/n: ")
                

            else:
                print("There are no services to delete!")

args = parser.parse_args()

if args.new:
    sdm_new = ServiceMaker()
    sdm_new.new_service()
    sdm_new.service_information()
    sdm_new.activate_service()
    sdm_new.write_service()

elif args.list:
    sdm_list = ServiceMaker()
    sdm_list.list_services()

elif args.delete:
    sdm_delete = ServiceMaker()
    sdm_delete.delete_service()

else:
    parser.parse_args(["-h"])
