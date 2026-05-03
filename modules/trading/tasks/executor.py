import subprocess

def run_command(cmd):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15
        )
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)