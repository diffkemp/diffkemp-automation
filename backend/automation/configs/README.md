# Library configuration files

The config files were originally designed by [Pavol Žáčik](https://github.com/zacikpa/diffkemp-analysis).
The config file's format was enhanced for this use-case.

## Format for version comparison

```yaml
type: versions
# Name of the analyzed project
name: libsodium
# URL of the git repository where the project is maintained
git: https://github.com/jedisct1/libsodium.git
# Id of the project on https://release-monitoring.org/, used for checking if
# new version was released
release-monitor-id: 1728
# Optional for tag filtering (comparing only certain versions/releases)
tag-filter: v\\d+.\\d+.\\d+
# Commands to run before the project can be built
config-commands:
  - ./autogen.sh
  - ./configure
# Additional Clang flags to use when building the project
clang-append:
  - -g
  - -O2
# Additional DiffKemp build options to use when building the project
build-options:
  - --no-opt-override
# The build target to use
target: no_test
# Functions to compare between each version pair
functions:
  - crypto_auth
  - crypto_auth_verify
```

## Format for commit comparison

```yaml
type: commits
# Name of the analyzed project
name: bpf-next
# Initial depth for cloning of the repository
depth: 500
# URL of the git repository where the project is maintained
git: https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git
# List of prefixes, commits starting with these prefixes and containing refactorization will be analyzed
commit-prefixes:
  - bpf
```
