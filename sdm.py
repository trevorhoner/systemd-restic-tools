import re
import json
from subprocess import run
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(prog='sdm', usage='%(prog)s [options]', 

                                 description='systemd manager', 
                                 epilog='Provides a fast way to efficiently manage and create systemd files',
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-n', '--new', action='store_true', 
                    help='makes new unit file')

parser.add_argument('-ns', '--new-system', nargs='?', const='new-system', 
                    default=None, metavar='-ns (system).service', help='new system unit')

parser.add_argument('-nys', '--new-system-activate', nargs='?', const='new-system', 
                    default=None, metavar='-nys (system).service', help='new system unit & activate')

parser.add_argument('-nu', '--new-user', nargs='?', const='new-user', 
                    default=None, metavar='-nu (user).service', help='new user unit')

parser.add_argument('-nyu', '--new-user-activate', nargs='?', const='new-user', 
                    default=None, metavar='-nyu (user).service', help='new user unit & activate')

parser.add_argument('-y', '--yes', action='store_true', 
                    help='automatically activates/deactivates service')

parser.add_argument('-l', '--list', action='store_true', 
                    help='list all created unit files')

parser.add_argument('-d', '--delete', nargs='?', const='delete', 
                    default=None, metavar='-d *.service',
                    help='deletes a unit file, -d [unit name]')

parser.add_argument('-dy', '--delete-deactivate', nargs='?', const='delete', 
                    default=None, metavar='-d *.service',
                    help='deletes & deactivates a unit file, -d [unit name]')
home = Path.home()

class ServiceMaker:
    """program that makes simple systemd services."""

    def __init__(self):
        """Select from: new, list, delete and write the name of the service"""
        self.data_path = Path("./data.json")
        #self.service_option =''

    def new_service(self):
        """Makes new service"""

        #Make a name for your new service
        print(f"\nMake a name for your new service.")
        print(f"\nWithout the suffix '*.service'")
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
        
        else:
            print(f"\nPlease pick 1, 2, or 3!")

        print(f"\nWhat is the name of your script? e.g. restic.sh")
        script_name = input(":")

        execute_script = run(["sudo","chmod", "+x", f"{path_directory}{script_name}"], check=True)

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
        print(f"\n1) /etc/systemd/system/ (System Unit)")
        print(f"2) sdm directory: sdm/services/ (System Unit)")
        print(f"3) home/.config/systemd/user/ (User Unit)")
        print(f"4) other location")
        self.service_option = int(input("\n:"))

        try:
            while self.service_option not in (1,2,3):
                print(f"Please pick 1, 2, or 3.")
                service_option = int(input("\nTry again: "))
        except ValueError:
            print(f"Please pick 1, 2, or 3")

        if self.service_option == 1:
            self.service_location = f"/etc/systemd/system/"
        elif self.service_option == 2:
            self.service_location = Path(__file__).resolve().parent / "services"
        elif self.service_option == 3:
            self.service_location = f"{home}/.config/systemd/user/"
        elif self.service_option == 4:
            print(f"Enter directory of .service file")
            self.service_location = input(f"\n:")
        else:
            None
            
        if self.service_option != 3:

            self.service_path = Path(f"{self.service_location}/{self.new_service}")
            self.data = f"{self.new_service}     S/U: System        Path: {self.service_path}"

            self.service_path.parent.mkdir(parents=True, exist_ok=True)
            self.service_path.write_text(service)

        else:

            self.service_path = Path(f"{self.service_location}{self.new_service}")
            self.data = f"{self.new_service}     S/U: User        Path: {self.service_path}"

            self.service_path.parent.mkdir(parents=True, exist_ok=True)
            self.service_path.write_text(service)

    def new_system_service(self):
        """Makes new system service for systemd"""

        if args.new_system != "new-system":
            self.new_service = f"{str(args.new_system)}.service"

        else:
            print(f"\nWhat would you like to name your system service?")
            self.new_service = f"{input(f"\n:")}.service"

        print(f"\nEnter a description for your service")
        description = input(":")

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

        execute_script = run(["sudo","chmod", "+x", f"{path_directory}{script_name}"], check=True)

        service = "[Unit]\n"
        service += f"{description}\n"
        service += "\n"
        service += "[Service]\n"
        service += f"ExecStart={path_directory}{script_name}\n"
        service += "\n"
        service += "[Install]\n"
        service += "WantedBy=multi-user.target"

        print(f"\nWhere do you wish to save your new system.service unit?")
        print(f"\n1) systemd directory: /etc/systemd/system/")
        print(f"2) sdm directory: sdm/services/")
        print(f"3) custom absolute-path: '/path/to/your/system.service'")
        choice = int(input(f"\n:"))

        if choice == 1:
            service_location = "/etc/systemd/system/"
            self.service_path = f"{service_location}/{self.new_service}"

        elif choice == 2:
            service_location = Path(__file__).resolve().parent / "services"
            self.service_path = Path(f"{service_location}/{self.new_service}")

        else:
            print(f"\nPlease define your custom absolute-path")
            service_location = input(":")
            self.service_path = f"{service_location}/{self.new_service}"

        self.data = f"{self.new_service}     S/U: System      Path: {self.service_path}"
        self.service_path.parent.mkdir(parents=True, exist_ok=True)
        self.service_path.write_text(service)

    def new_user_service(self):
        """Makes new user service"""

        self.new_service = str(args.new_user)

        print(f"\nEnter a description for your service")
        description = input(":")

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

        execute_script = run(["sudo","chmod", "+x", f"{path_directory}{script_name}"], check=True)

        service = "[Unit]\n"
        service += f"{description}\n"
        service += "\n"
        service += "[Service]\n"
        service += f"ExecStart={path_directory}{script_name}\n"
        service += "\n"
        service += "[Install]\n"
        service += "WantedBy=multi-user.target"

        service_location = f"{home}/.config/systemd/user/"

        self.service_path = Path(f"{service_location}{self.new_service}")
        self.data = f"{self.new_service}     S/U: User      Path: {self.service_path}"

        self.service_path.parent.mkdir(parents=True, exist_ok=True)
        self.service_path.write_text(service)
        
        print(f"\nDo you wish to start and enable {self.new_service}?")
        choice = input("y/n: ")

        if choice == "y":
            run(["systemctl", "--user", "daemon-reload"], check=True, )
            run(["systemctl", "--user", "enable", "--now", self.new_service], check=True, )

        else:
            return None

    def activate_service(self):
        """Activates new unit file"""

        if args.new:

            #Activates system unit
            if self.service_option != 3:
                run(["sudo", "systemctl", "link", self.service_path], check=True)
                run(["sudo", "systemctl", "daemon-reload"], check=True)
                run(["sudo", "systemctl", "enable", self.new_service], check=True)

            else:
                #Activates user unit
                run(["systemctl", "--user", "daemon-reload"], check=True, )
                run(["systemctl", "--user", "enable", "--now", self.new_service], check=True, )

        if args.new_user:

            print(f"\nDo you wish to start and enable {self.new_service}?")
            choice = input("y/n: ")

            if choice == "y":
                run(["systemctl", "--user", "daemon-reload"], check=True, )
                run(["systemctl", "--user", "enable", "--now", self.new_service], check=True, )

            else:
                return None

        if args.new_system:
            
            print(f"\nDo you wish to start and enable {self.new_service}?")
            choice = input("y/n: ")

            if choice == "y":
                run(["sudo", "systemctl", "link", self.service_path], check=True)
                run(["sudo", "systemctl", "daemon-reload"], check=True)
                run(["sudo", "systemctl", "enable", "--now",  self.new_service], check=True)

            else:
                return None

        if args.new_system_activate:

            run(["sudo", "systemctl", "link", self.service_path], check=True)
            run(["sudo", "systemctl", "daemon-reload"], check=True)
            run(["sudo", "systemctl", "enable", "--now",  self.new_service], check=True)

        elif args.new_user_activate:

            run(["systemctl", "--user", "daemon-reload"], check=True, )
            run(["systemctl", "--user", "enable", "--now", self.new_service], check=True, )

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

            if json_data == []:
                print(f"\nYou have no services to list!")

            else:

                count = 1
                for service in json_data:
                    print(f"\n[{count}] {service}")
                    count += 1

        else:
            print("\nThere is no data.json file!")
        
    def delete_service(self):
        """deletes service from list"""

        #If no service is passed as an argument, you delete from a list
        if args.delete == "delete":
            if self.data_path.exists():

                with open(self.data_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)


                if json_data == []:
                    print(f"\nThere are no services to delete!")

                else:
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
                    
                    #Checks if the user wants to delete said service
                    print(f"\nAre you sure you want to delete {service_name}?")
                    self.fail_choice = input(f"y/n: ").lower().strip()

                    #Need to make separate entries for user and system units
                    if self.fail_choice == 'y':

                        #Needs to check if a system or user service file
                        run(["sudo", "systemctl", "stop", service_name])
                        #run(["sudo", "systemctl", "--user", "stop", service_name], check=True)
                        #run(["sudo", "systemctl", "--user", "kill", "--signal=SIGKILL", service_name], check=True)
                        run(["sudo", "systemctl", "disable", service_name])
                        run(["sudo", "systemctl", "daemon-reload"])
                        run(["sudo","rm","-r", delete_path], check=True)

                        #Removing service from data.json
                        with open(self.data_path, "r", encoding="utf-8") as f:
                            json_data = json.load(f)

                        del json_data[self.choice-1]

                        with open(self.data_path, "w", encoding="utf-8") as f:
                            json.dump(json_data, f, ensure_ascii=False, indent=2)

                    elif self.fail_choice == 'n':
                        return None

                    else:
                        print("\nNot a valid choice.")
                        print("Please enter (y)es or (n)o")
                        self.fail_choice = input(f"y/n: ")
                

            else:
                print("There is no data.json file!")

    #def deactivate_service(self):
    #    """Deactivates system or user service"""

    #    #if args.delete:

    #    #if args.delete_deactivate:
    #    #if args.delete_deactivate:

    #        with open(self.data_path, "r", encoding="utf-8") as f:
    #            json_data = json.load(f)

    #        count = 0
    #        for service in json_data:
    #            service_name = re.search(f"{args.delete}.service",json_data[count])[0]
    #            system_or_user = re.search('(?<=S/U: )\\D{4,6}',json_data[count])[0]

    #            if service_name == True and system_or_user == "System":
    #                delete_path = Path(re.search('(?<=Path: )\\D+',json_data[count])[0])
    #                run(["sudo", "systemctl", "stop", service_name], check=True)
    #                run(["sudo", "systemctl", "disable", service_name], check=True)
    #                run(["sudo", "systemctl", "daemon-reload"], check=True)
    #                run(["sudo","rm","-r", delete_path], check=True)
    #                del json_data[count]

    #                print(f"\nSystem service: {service_name} has been deleted!")

    #            elif service_name == True and system_or_user == "User":
    #                delete_path = Path(re.search('(?<=Path: )\\D+',json_data[count])[0])
    #                run(["sudo", "systemctl", "stop", service_name], check=True)
    #                run(["sudo", "systemctl", "disable", service_name], check=True)
    #                run(["sudo", "systemctl", "daemon-reload"], check=True)
    #                run(["sudo","rm","-r", delete_path], check=True)
    #                del json_data[count]

    #                print(f"\nUser service: {service_name} has been deleted!")
    #            else:
    #                count += 1
    #            
    #        with open(self.data_path, "w", encoding="utf-8") as f:
    #            json.dump(json_data, f, ensure_ascii=False, indent=2)  


args = parser.parse_args()

if args.new:
    sdm_new = ServiceMaker()
    sdm_new.new_service()
    sdm_new.service_information()
    sdm_new.activate_service()
    sdm_new.write_service()

elif args.new_system:
    sdm_new_system = ServiceMaker()
    sdm_new_system.new_system_service()
    sdm_new_system.write_service()
    sdm_new_system.activate_service()

elif args.new_user:
    sdm_new_user = ServiceMaker()
    sdm_new_user.new_user_service()

elif args.new_system_activate:
    sdm_new_system_activate = ServiceMaker()
    sdm_new_system_activate.new_system_service()

elif args.new_user_activate:
    sdm_new_user_activate = ServiceMaker()
    sdm_new_user_activate.new_user_service()
    sdm_new_user_activate.activate_service()

elif args.list:
    sdm_list = ServiceMaker()
    sdm_list.list_services()

elif args.delete:
    sdm_delete = ServiceMaker()
    sdm_delete.delete_service()

elif args.delete and args.yes:
    sdm_delete_yes = ServiceMaker()
    sdm_delete_yes.delete_service()

else:
    parser.parse_args(["-h"])
