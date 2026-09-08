import os

def check_file(path):
    print(f"--- {path} ---")
    if os.path.exists(path):
        with open(path) as f:
            print(f.read())
    else:
        print("Missing!")

check_file("frontend/staff/login.html")
check_file("frontend/staff/dashboard.html")
