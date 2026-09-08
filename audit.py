import os

def check_file(path):
    print(f"--- {path} ---")
    if os.path.exists(path):
        with open(path) as f:
            print(f.read())
    else:
        print("Missing!")

check_file("backend/app/api/registration.py")
check_file("backend/app/core/queue.py")
check_file("backend/app/api/auth.py")
check_file("backend/app/api/staff.py")
check_file("backend/app/server.py")
