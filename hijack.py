import argparse
import os
import subprocess
import requests
import tempfile

SUPPORTED_FILES = {
    "package.json": "npm",
    "package-lock.json": "npm",
    "requirements.txt": "pip",
    "composer.json": "composer",
    "composer.lock": "composer",
    ".composer/composer.json": "composer",
    "vendor/composer/installed.json": "composer",
    "pom.xml": "mvn",
    "Gemfile": "rubygems",
    "Gemfile.lock": "rubygems",
    "pyproject.toml": "pip",
    "poetry.lock": "pip",
    "yarn.lock": "npm"
}

def parse_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    return [line.split()[-1] for line in lines if line.strip().startswith("[exposed-dependency-configs]")]

def download_file(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        filename = os.path.basename(url.split('?')[0])
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        return temp_path, filename
    except Exception as e:
        print(f"[!] Failed to download {url}: {e}")
        return None, None

def detect_package_system(filename):
    for name, system in SUPPORTED_FILES.items():
        if filename.endswith(name):
            return system
    return None

def run_confused(filepath, system):
    try:
        cmd = ["confused", "-l", system, filepath]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] confused failed on {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Path to file with results')
    parser.add_argument('-u', '--url', help='Single result URL')
    args = parser.parse_args()

    urls = []
    if args.file:
        urls = parse_file(args.file)
    elif args.url:
        urls = [args.url]
    else:
        print("[-] Provide either -f <file> or -u <url>")
        return

    for url in urls:
        path, name = download_file(url)
        if path and name:
            system = detect_package_system(name)
            if system:
                print(f"[*] Scanning {name} as {system} package")
                run_confused(path, system)
            else:
                print(f"[!] Unsupported file type: {name}")

if __name__ == "__main__":
    main()
