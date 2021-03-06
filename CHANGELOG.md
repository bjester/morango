# Release Notes

List of the most important changes for each release.

## 0.5.5

- Allow MAC address to be overridden by envvar for instance_id calculation

## 0.5.4

- Don't die on session deletion when transfersession.records_total is None

## 0.5.3

- Cache the instance ID on app load, to avoid database lockup issues

## 0.5.2

- Split up `SyncClient` and fix bandwidth tracking (https://github.com/learningequality/morango/pull/85)

## 0.5.1

- Deserialization improvements (https://github.com/learningequality/morango/pull/84)

## 0.5.0

- Increase the stability of the Instance ID so it doesn't change as frequently (https://github.com/learningequality/morango/pull/83)

## 0.4.11

- Add serialized isolation level decorator for postgres transactions (https://github.com/learningequality/morango/pull/77)

## 0.4.10

- Bug fixes and performance improvements
- Enforce serializable isolation connection for postgres

## 0.4.9

- Fix for not sending correct cert chain

## 0.4.8

- Retry logic to better handle flaky network connections
- Introduce ALLOW_CERTIFICATE_PUSHING to support Cloud Kolibri
- Overall project refactor

## 0.4.7

- Small fixes

## 0.4.6

- Switch from file-based caching to Django's lru_cache for sqlite max vars

## 0.4.5

- fixes issue where GET requests with body payload fails

## 0.4.4

- adds gzipping capability on buffer post requests
- parametrizes chunk size to allow it to be set when initiating sync sessions

## 0.4.3

- remove unused files in dist

## 0.4.2

- Added fix for writing CACHE file on windows

## 0.4.1

- Added fix for writing CACHE file to user directory

## 0.4.0

- Added inverse CSR endpoints for pushing data to a server
- various performance improvements
- allow for hard deletion which purges data and is able to propagate to other devices

## 0.3.3

- Add transactions around queuing into buffer and dequeuing into store

## 0.3.2

- Mute signals before deserialization/saving store models

## 0.3.1

- removed logic of loading scope definition fixtures (delegated to main application)

## 0.3.0

- added support for postgres database backend

## 0.2.4

## 0.2.3

## 0.2.2

## 0.2.1

## 0.2.0

## 0.1.1

## 0.1.0

- First working version for morango

## 0.0.2: content-curation compatibility!

- make requirements more flexible

## 0.0.1: the initial release!

- Add in model name to uuid calc.
