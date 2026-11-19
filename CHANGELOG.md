# Changelog

## Before the MaHaHe fork

Releases of robrotheram/taiga-contrib-openid-auth, kept for reference.

## 1.0.0 (2026-11-19)


### Features

* release images to GHCR for Taiga 6.10 ([#7](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/7)) ([ba1dc2b](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/ba1dc2b8d63cd2c08deb762328b01e0fc65e9b08))


### Bug Fixes

* **back:** support Taiga 6.10 and honour every OPENID_* variable ([#4](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/4)) ([f0e8878](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/f0e8878bef10974d1b4e0df5a35681b38f849a81))
* **front:** build the plugin in the image and extend Taiga 6.10's config ([#5](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/5)) ([f82bf35](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/f82bf35f380cefe2e632afe3016ac98502b6774e))

### 0.0.1 (2018-08-07)
- Compatible with Taiga 3.0.0
- Initial release.
- Forked from https://github.com/taigaio/taiga-contrib-github-auth

### 0.0.2 (2019-04-02)
- Compatible with Taiga 4.2.1
- Fixed several references to the Github contrib plugin for Taiga.
- Fixed missing OpenID button image.
- Added the ability to pass the access token to the front end to support authenticating reverse proxies like [keycloak-gatekeeper](https://github.com/keycloak/keycloak-gatekeeper).

### 0.0.2 (2019-04-02)
- Compatible with Taiga 4.2.1
- Fixed several references to the Github contrib plugin for Taiga.
- Fixed missing OpenID button image.
- Added the ability to pass the access token to the front end to support authenticating reverse proxies like [keycloak-gatekeeper](https://github.com/keycloak/keycloak-gatekeeper).


### 6.0.2 (2021-02-20)
- Compatible with Taiga 6.0.2
- Mereged work done by @cristianlazarop 
- Added back in required features (user signups)
- Breaking change. To allow registrations backend needs to have 'PUBLIC_REGISTER_ENABLED=True' see Readme.md
- Added Docker Files to allow the plugin to work with the offical taiga images for 6

### 6.0.7 (2021-03-31)
- Added username fallback 
- Configurable Fields

### 6.0.8 (2021-04-19)
- Added Scope paramater to openid request
