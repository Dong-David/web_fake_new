import subprocess
import sys

def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

if __name__ == "__main__":
    run_script("createReal.py")

    run_script("createFake.py")

    print("Auto creation of Real and Fake articles is done.")
