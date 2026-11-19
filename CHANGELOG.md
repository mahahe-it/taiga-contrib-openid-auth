# Changelog

## Before the MaHaHe fork

Releases of robrotheram/taiga-contrib-openid-auth, kept for reference.

## [1.0.4](https://github.com/mahahe-it/taiga-contrib-openid-auth/compare/1.0.3...1.0.4) (2026-11-19)


### Bug Fixes

* **front:** build the plugin with gulp 5, CoffeeScript 2 and uglify 3 ([#55](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/55)) ([4b90b28](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/4b90b28e9920239d49e985c119a2d44712bb0bd1))
* **front:** compile the template with pug instead of jade ([#57](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/57)) ([5f5022d](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/5f5022d662c99dae6d83778df515296457601c50))

## [1.0.3](https://github.com/mahahe-it/taiga-contrib-openid-auth/compare/1.0.2...1.0.3) (2026-11-19)


### Bug Fixes

* **back:** do not fail on import when the plugin is not installed ([#52](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/52)) ([6b31c8e](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/6b31c8ef42a513159572f3f6a38b54f2e6b671bd))
* **back:** reject filter claims that are not strings ([#49](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/49)) ([bccd6c2](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/bccd6c2eaaf71d22e87151f25101b1e4ec6dafd2))
* **back:** treat settings set to None or empty as unset ([#50](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/50)) ([70ba56a](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/70ba56a564ecc81d968d0d195b0ccbf296352d5d))
* **images:** retry the front config after a failure and warn on missing settings ([#53](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/53)) ([de15502](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/de1550285a2197eadcd67323ee33ff20d84b8da5))

## [1.0.2](https://github.com/mahahe-it/taiga-contrib-openid-auth/compare/1.0.1...1.0.2) (2026-11-19)


### Bug Fixes

* **back:** refuse missing userinfo claims instead of failing with a 500 ([#46](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/46)) ([ae571b7](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/ae571b789eb33620f96427c7c1fe62a1d9912c63))
* **back:** time out requests to the identity provider ([#47](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/47)) ([04b0d05](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/04b0d0560cea5062d055b6552634bfc491aa59a4))
* **front:** accept the invitation when signing in from it ([#43](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/43)) ([de1618b](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/de1618b20a2cf34010be1fecc1b43a0decf5b981))
* **front:** load the plugin script and image under TAIGA_SUBPATH ([#45](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/45)) ([d24dff7](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/d24dff708cd87f16bdb3807c7e1253fd1b0616df))

## [1.0.1](https://github.com/mahahe-it/taiga-contrib-openid-auth/compare/1.0.0...1.0.1) (2026-11-19)


### Bug Fixes

* **back:** link to an existing account only if the email is verified ([#41](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/41)) ([9a2f709](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/9a2f7091e98283f891e5e4f489d8fb38345863a1))
* **back:** make access token login opt-in ([#42](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/42)) ([68f2cba](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/68f2cba26e6dac51fde4129e23be8a2afa261720))
* **front:** send and verify the OAuth state on login ([#39](https://github.com/mahahe-it/taiga-contrib-openid-auth/issues/39)) ([7f0c7be](https://github.com/mahahe-it/taiga-contrib-openid-auth/commit/7f0c7bef50c55bddb3b221ce7e133a7548ee2c0b))

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
