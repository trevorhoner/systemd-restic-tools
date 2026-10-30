from subprocess import call
from pathlib import Path

def choose_option():
    print(f"\nWelcome to systemd service maker!")
    print(f"What would you like to do?")
    print(f"\n1) Make new service")
    print(f"2) List services")
    print(f"3) Delete service\n")
    choice = input(":")
    try:
        return int(choice)
    except ValueError:
        print(f"\nNot a valid option. Please choose 1, 2, or 3!")

class ServiceMaker:
    """program that makes simple systemd services."""

    def __init__(self, choice, service_name=''):
        """Select from: new, list, delete and write the name of the service"""
        self.choice = choice
        self.service_name = service_name

    def new_service(self):
        """Makes new service"""
        print(f"\nEnter a description for your service")
        description = input(":")

        print(f"\nWhere is your script or program located?")
        print(f"\n1) usr/local/bin/")
        print(f"2) usr/sbin/")
        print(f"3) Other location")
        path_option = input(":")

        print(f"\nWhat is the name of your script? e.g. restic.sh or resctic.py")
        script_name = input(":")

choice = choose_option()
systemd_action = ServiceMaker(choice)

if choice == 1:
    systemd_action.new_service()

else: 
    None
