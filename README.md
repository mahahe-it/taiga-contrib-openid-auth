# taiga-contrib-openid-auth

OpenID Connect login for [Taiga](https://taiga.io) 6: users sign in through
Keycloak or any other OpenID Connect provider, and can be limited to members of
given groups. Based on [taiga-contrib-github-auth](https://github.com/taigaio/taiga-contrib-github-auth).

Maintained by [MaHaHe](https://github.com/mahahe-it). It started as a fork of
[robrotheram/taiga-contrib-openid-auth](https://github.com/robrotheram/taiga-contrib-openid-auth),
which is no longer maintained.

## Images

Two images extend the official taigaio ones with the plugin and nothing else, so
every upstream variable and customisation keeps working:

| Image | Base | Tags |
|---|---|---|
| `ghcr.io/mahahe-it/taiga-back-openid` | `taigaio/taiga-back:6.10.2` | `6.10.2`, `6.10.2-openid.<version>` |
| `ghcr.io/mahahe-it/taiga-front-openid` | `taigaio/taiga-front:6.10.3` | `6.10.3`, `6.10.3-openid.<version>` |

Each image is tagged with the version of its own base (taigaio versions back and
front independently). `<base>` moves to the newest plugin release built on that
base; `<base>-openid.<version>` never changes. There is no `latest`. Every plugin
release rebuilds both images. Images are `linux/amd64`, like their bases.

Use the back image for **taiga-back and taiga-async**: async loads the same
settings, and with `ENABLE_OPENID=True` it needs the plugin installed.

### Back variables (taiga-back, taiga-async)

| Variable | Default | |
|---|---|---|
| `ENABLE_OPENID` | `False` | `True` installs the plugin |
| `OPENID_TOKEN_URL` | | token endpoint, e.g. `https://<keycloak>/realms/<realm>/protocol/openid-connect/token` |
| `OPENID_USER_URL` | | userinfo endpoint, e.g. `https://<keycloak>/realms/<realm>/protocol/openid-connect/userinfo` |
| `OPENID_CLIENT_ID` | | |
| `OPENID_CLIENT_SECRET` | | |
| `OPENID_SCOPE` | `openid email` | add `profile` for Keycloak to send the username and full name |
| `OPENID_ID_FIELD` | `sub` | claim with the user's unique id |
| `OPENID_USERNAME_FIELD` | `preferred_username` | then `preferred_username`, `full_name`, `username`, `email` are tried in order |
| `OPENID_FULLNAME_FIELD` | `name` | |
| `OPENID_EMAIL_FIELD` | `email` | |
| `OPENID_FILTER_FIELD` | | claim to filter on, e.g. `groups` (a list or a single string) |
| `OPENID_FILTER` | | allowed values, comma separated, e.g. `taiga_users, taiga_admins` |

`PUBLIC_REGISTER_ENABLED=True` (upstream variable) lets the plugin create
accounts on the first login; without it only existing users can sign in. A user
whose email matches an existing Taiga account is linked to that account.

The image selects its settings with `DJANGO_SETTINGS_MODULE=settings.openid`,
which loads upstream's `settings/config.py` and adds the plugin. A `config.py`
mounted over upstream's keeps working.

### Front variables (taiga-front)

| Variable | Default | |
|---|---|---|
| `ENABLE_OPENID` | `false` | `true` adds the login button |
| `OPENID_URL` | | authorization endpoint, e.g. `https://<keycloak>/realms/<realm>/protocol/openid-connect/auth` |
| `OPENID_CLIENT_ID` | | |
| `OPENID_NAME` | `OpenID` | the button reads "Sign in with `<name>`" |
| `OPENID_SCOPE` | `openid email` | same value as the back's |

The image adds these settings and the plugin to the `conf.json` that upstream
generates at the first start. A `conf.json` you mount yourself is left alone:
add `openidAuth`, `openidClientId`, `openidName`, `openidScope` and
`"plugins/openid-auth/openid-auth.json"` in `contribPlugins` to it.

### Keycloak

Create a confidential OpenID Connect client (client authentication on, standard
flow) with the redirect URI `https://<your-taiga>/*`. To filter by group, add a
"Group Membership" mapper to the client with the token claim name `groups`,
"Full group path" off and "Add to userinfo" on, then set
`OPENID_FILTER_FIELD=groups` and `OPENID_FILTER=<group>`.

[`e2e/compose.yaml`](e2e/compose.yaml) is a complete, tested setup with Keycloak
([`e2e/keycloak/realm-taiga.json`](e2e/keycloak/realm-taiga.json)), based on
[taiga-docker](https://github.com/taigaio/taiga-docker).

## Manual installation

Back, in taiga-back's virtualenv:

```bash
pip install ./back
```

and in the settings module:

```python
INSTALLED_APPS += ["taiga_contrib_openid_auth"]
OPENID_USER_URL = "https://<keycloak>/realms/<realm>/protocol/openid-connect/userinfo"
OPENID_TOKEN_URL = "https://<keycloak>/realms/<realm>/protocol/openid-connect/token"
OPENID_CLIENT_ID = "<client id>"
OPENID_CLIENT_SECRET = "<client secret>"
```

Front: build the plugin (`cd front && npm ci && npx gulp copy-config copy-images compile`),
copy `front/dist/` to `<taiga-front>/plugins/openid-auth/`, and add to `conf.json`:

```json
{
  "openidAuth": "https://<keycloak>/realms/<realm>/protocol/openid-connect/auth",
  "openidName": "<name for the login button>",
  "openidClientId": "<client id>",
  "openidScope": "openid email profile",
  "contribPlugins": ["plugins/openid-auth/openid-auth.json"]
}
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md): `just build`, `just test-back`,
`just test-images` and `just e2e` build the images and run the unit, image and
end-to-end tests.

## Contributions

My thanks to all the people who have added to the plugin
- @cristianlazarop
- @swedishborgie
- @baloo42
- @carneirofc
- @robrotheram
- The whole taiga team who wrote the github plugin that this plugin is based off.
