import requests
import json
import argparse
from urllib.parse import urlparse
import os

def download_and_convert(url, output_dir="."):
    """
    Downloads a package-lock.json from the given URL, extracts top-level dependencies,
    and creates a corresponding package.json file.
    """

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        lock_data = response.json()
    except Exception as e:
        print(f"❌ Failed to fetch or parse JSON from {url}: {e}")
        return

    # Generate safe filename based on domain name
    domain = urlparse(url).netloc.replace(".", "_").replace(":", "_")
    filename = os.path.join(output_dir, f"package_{domain}.json")

    # Initialize package.json structure
    package_json = {
        "name": f"restored-package-{domain}",
        "version": "1.0.0",
        "dependencies": {},
        "devDependencies": {}
    }

    # Parse dependencies
    dependencies = lock_data.get("dependencies", {})
    for name, info in dependencies.items():
        version = info.get("version", "")
        if info.get("dev", False):
            package_json["devDependencies"][name] = version
        else:
            package_json["dependencies"][name] = version

    # Remove devDependencies if empty
    if not package_json["devDependencies"]:
        del package_json["devDependencies"]

    # Save to file
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved: {filename}")
    except Exception as e:
        print(f"❌ Failed to save {filename}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Convert package-lock.json from a URL into package.json format.")
    parser.add_argument("-u", "--url", help="URL to package-lock.json")
    parser.add_argument("-f", "--file", help="File containing list of URLs (one per line)")
    parser.add_argument("-o", "--output", help="Output directory", default=".")

    args = parser.parse_args()

    if args.url:
        download_and_convert(args.url, args.output)
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
            for url in urls:
                download_and_convert(url, args.output)
        except Exception as e:
            print(f"❌ Failed to read URL list file: {e}")
    else:
        print("⚠️ Please specify either -u URL or -f FILE")

if __name__ == "__main__":
    main()
