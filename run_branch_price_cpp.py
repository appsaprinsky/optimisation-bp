import subprocess
executable_path = "./branch-and-bound.out"
try:
    result = subprocess.run(executable_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Output of the executable:")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("Error occurred while running the executable:")
    print(e.stderr)
