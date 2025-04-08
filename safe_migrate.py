import os
import subprocess

def run_command(command):
    """ Helper function to run shell commands """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = process.communicate()
    if process.returncode != 0:
        print(f"Error occurred: {err.decode('utf-8')}")
    else:
        print(out.decode('utf-8'))

def safe_migrate():
    """ Script to reset and migrate migrations safely """

    # 1. Rollback migrations for socialaccount and sites
    print("Rolling back migrations...")
    run_command('python manage.py migrate socialaccount zero')
    run_command('python manage.py migrate sites zero')

    # 2. Reapply migrations for sites first, then socialaccount
    print("Reapplying migrations for sites...")
    run_command('python manage.py migrate sites')

    print("Reapplying migrations for socialaccount...")
    run_command('python manage.py migrate socialaccount')

    # 3. Show all migrations to verify the state
    print("Verifying migrations are applied correctly...")
    run_command('python manage.py showmigrations')

if __name__ == "__main__":
    print("Starting migration reset process...")
    safe_migrate()
    print("Migration reset and application complete.")
