# nuclei-dependency-confusion
#### Overview:
A comprehensive Nuclei template for detecting exposed dependency configuration files (e.g., `package.json`, `composer.json`, etc.). When combined with the [confused](https://github.com/knavesec/confused) tool, it helps identify potential dependency confusion vulnerabilities.
#### Running Nuclei Scan
```
nuclei -u https://company.com -t exposed-dependency-configs.yaml
```
#### Scan a list of live HTTP services:
```
nuclei -l alive_http_services.txt -t exposed-dependency-configs.yaml -o deps_exposed_results.txt
```
#### Sample Output
```
[exposed-dependency-configs] [http] [medium] https://tesla.com/package.json
[exposed-dependency-configs] [http] [medium] https://dev.tesla.com/package-lock.json
[exposed-dependency-configs] [http] [medium] http://admin.dev.php.tesla.com/vendor/composer/installed.json
[exposed-dependency-configs] [http] [medium] https://portal.qa.tesla.com/composer.json
```
## Confused Installation & Usage

#### Installation
```bash
git clone https://github.com/knavesec/confused && \
cd confused && \
go get github.com/knavesec/confused && \
go build && \
sudo cp confused /usr/local/bin/

```
#### Usage
```
confused [-l systempackage] packagefile

Options:
  -l string    Package repository system. Possible values: "pip", "npm", "composer", "mvn", "rubygems" (default: "npm")
  -s string    Comma-separated list of known-secure namespaces. Wildcards supported.
  -v           Verbose output
```
#### Example:
```
curl -k -L -o package.json https://tesla.com/package.json
confused -l npm package.json
```
#### With known-secure namespaces:
```
confused -l npm -s "@company/*,@internal/*" package.json
```
#### Pro Tips
Converting `package-lock.json` to `package.json`:

Since **confused** only accepts `package.json` files, use the included `package.py` converter for `package-lock.json` files:
```
python package.py -u https://tesla.com/package-lock.json
# Output: ✅ Saved: .\package_tesla_com.json
confused -l npm package_tesla_com.json
```
---
#### Automation Dependency Hijacking
```
python3 hijack.py -h
usage: hijack.py [-h] [-f FILE] [-u URL] [-o OUTPUT] [-s]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to file with results
  -u URL, --url URL     Single result URL
  -o OUTPUT, --output OUTPUT
                        Write report to file
  -s, --silent          Show only results with issues
```
#### Run scanning:
```
python3 hijack.py -u https://tesla.com/package-lock.json -s
python3 hijack.py -f deps_exposed_results.txt -o confused_results.txt -s
```
#### Sample Output
```
===== CONFUSED SCAN REPORT =====

###### mail.example.com/composer.json ######
[*] All packages seem to be available in the public repositories.

In case your application uses private repositories please make sure that those namespaces in
public repositories are controlled by a trusted party.

###### api.example.com/composer.lock ######
[*] All packages seem to be available in the public repositories.

In case your application uses private repositories please make sure that those namespaces in
public repositories are controlled by a trusted party.
```
