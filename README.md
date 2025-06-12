# nuclei-dependency-confusion
A comprehensive Nuclei template for detecting exposed dependency configuration files and integration with [confused](https://github.com/visma-prodsec/confused) that identifying potential dependency confusion vulnerabilities.
```
nuclei -u https://company.com -t ./exposed-dependency-configs.yaml
nuclei -l alive_http_services.txt -t ./exposed-dependency-configs.yaml
```
Installation
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
confused -l npm package.json
```
With known-secure namespaces:
```
confused -l npm -s "@company/*,@internal/*" package.json
```
