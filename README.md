# nuclei-dependency-confusion
A comprehensive Nuclei template for detecting exposed dependency configuration files and integration with [confused](https://github.com/visma-prodsec/confused) that identifying potential dependency confusion vulnerabilities.
```
nuclei -u https://company.com -t ./exposed-dependency-configs.yaml
nuclei -l alive_http_services.txt -t ./exposed-dependency-configs.yaml
```
Sample Output
```
[exposed-dependency-configs] [http] [medium] https://tesla.com/package.json
[exposed-dependency-configs] [http] [medium] https://dev.tesla.com/package-lock.json
[exposed-dependency-configs] [http] [medium] http://admin.dev.php.tesla.com/vendor/composer/installed.json
[exposed-dependency-configs] [http] [medium] https://portal.qa.tesla.com/composer.json
```
Installation Confused
```
git clone https://github.com/visma-prodsec/confused
cd confused
go build
```
Usage
```
confused [-l systempackage] packagefile

Usage of confused:

  -l string    Package repository system. Possible values: "pip", "npm", "composer", "mvn", "rubygems" (default "npm")
  -s string    Comma-separated list of known-secure namespaces. Supports wildcards
  -v           Verbose output
```
Sample command:
```
curl -k -L -o package.json https://tesla.com/package.json
confused -l npm package.json
```
With known-secure namespaces:
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

