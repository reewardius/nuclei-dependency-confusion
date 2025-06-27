import argparse
import os
import subprocess
import requests
import tempfile
import json
import urllib3
from urllib.parse import urlparse

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        filename = os.path.basename(url.split('?')[0])
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        return temp_path, filename
    except Exception as e:
        print(f"[!] Failed to download {url}: {e}")
        return None, None

def convert_lock_to_package(lock_path, domain):
    try:
        with open(lock_path, 'r', encoding='utf-8') as f:
            lock_data = json.load(f)

        package_json = {
            "name": f"restored-package-{domain}",
            "version": "1.0.0",
            "dependencies": {},
            "devDependencies": {}
        }

        dependencies = lock_data.get("dependencies", {})
        for name, info in dependencies.items():
            version = info.get("version", "")
            if info.get("dev", False):
                package_json["devDependencies"][name] = version
            else:
                package_json["dependencies"][name] = version

        if not package_json["devDependencies"]:
            del package_json["devDependencies"]

        package_path = os.path.join(tempfile.gettempdir(), f"package_{domain}.json")
        with open(package_path, "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2, ensure_ascii=False)

        return package_path
    except Exception as e:
        print(f"[!] Failed to convert lock file: {e}")
        return None

def detect_package_system(filename):
    for name, system in SUPPORTED_FILES.items():
        if filename.endswith(name):
            return system
    return None

def run_confused(filepath, system):
    try:
        cmd = ["confused", "-l", system, filepath]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        output = e.stdout if e.stdout else ""
        error = e.stderr if e.stderr else str(e)
        return f"{output}\n[!] confused failed: {error}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Path to file with results')
    parser.add_argument('-u', '--url', help='Single result URL')
    parser.add_argument('-o', '--output', help='Write report to file')
    args = parser.parse_args()

    urls = []
    if args.file:
        urls = parse_file(args.file)
    elif args.url:
        urls = [args.url]
    else:
        print("[-] Provide either -f <file> or -u <url>")
        return

    report = []
    for url in urls:
        parsed = urlparse(url)
        domain = parsed.netloc
        path, name = download_file(url)
        header = f"\n###### {domain}{parsed.path} ######"

        if path and name:
            if name == "package-lock.json":
                print(f"[*] Converting {name} to package.json for scanning")
                new_path = convert_lock_to_package(path, domain.replace('.', '_'))
                if new_path:
                    output = run_confused(new_path, "npm")
                    report.append(f"{header}\n{output.strip()}")
                else:
                    msg = f"[!] Failed to convert {name}"
                    print(msg)
                    report.append(f"{header}\n{msg}")
                continue

            system = detect_package_system(name)
            if system:
                print(f"[*] Scanning {name} as {system} package")
                output = run_confused(path, system)
                report.append(f"{header}\n{output.strip()}")
            else:
                msg = f"[!] Unsupported file type: {name}"
                print(msg)
                report.append(f"{header}\n{msg}")
        else:
            msg = f"[!] Failed to download {url}"
            print(msg)
            report.append(f"{header}\n{msg}")

    final_report = "\n===== CONFUSED SCAN REPORT =====\n" + "\n".join(report)
    print(final_report)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(final_report)
            print(f"[+] Report saved to {args.output}")
        except Exception as e:
            print(f"[!] Failed to write report: {e}")

if __name__ == "__main__":
    main()
