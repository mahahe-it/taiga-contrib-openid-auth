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
| [`ghcr.io/mahahe-it/taiga-back-openid`](https://github.com/orgs/mahahe-it/packages/container/package/taiga-back-openid) | `taigaio/taiga-back` | `<base>`, `<base>-openid.<version>` |
| [`ghcr.io/mahahe-it/taiga-front-openid`](https://github.com/orgs/mahahe-it/packages/container/package/taiga-front-openid) | `taigaio/taiga-front` | `<base>`, `<base>-openid.<version>` |

Each image is tagged with the version of its own base (taigaio versions back and
front independently): `TAIGA_BACK_VERSION` in
[`docker/back/Dockerfile`](docker/back/Dockerfile) and `TAIGA_FRONT_VERSION` in
[`docker/front/Dockerfile`](docker/front/Dockerfile), kept current by Renovate;
the package pages list the published tags. `<base>` moves to the newest plugin
release built on that base; `<base>-openid.<version>` never changes. There is no
`latest`. Every plugin release rebuilds both images. Images are `linux/amd64`,
like their bases.

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
| `OPENID_REQUIRE_VERIFIED_EMAIL` | `True` | link to an existing account only if the provider sends `email_verified: true` |
| `OPENID_TOKEN_AUTH_METHOD` | `client_secret_post` | `client_secret_basic` sends the client credentials as HTTP Basic auth |
| `OPENID_TIMEOUT` | `10` | seconds to wait for the token and userinfo endpoints |
| `OPENID_ALLOW_ACCESS_TOKEN` | `False` | accept an access token from the front (`/login?access_token=…`), see below |

The userinfo response must carry the id (`OPENID_ID_FIELD`) and email
(`OPENID_EMAIL_FIELD`) claims, or the login is refused with an error naming the
missing claim. Without a full name claim (Keycloak sends `name` only with the
`profile` scope), the username is used.

`PUBLIC_REGISTER_ENABLED=True` (upstream variable) lets the plugin create
accounts on the first login; without it only existing users can sign in.

On the first OpenID login of a user whose email matches an existing Taiga
account, the identity is linked to that account, but only if the provider marks
the email as verified (`email_verified` claim). Otherwise the login is refused:
whoever controls an unverified email would get that account, an admin's too.
Users already linked, and new users, are not affected.

Keycloak sends `email_verified: false` for users created by an admin unless
"Email verified" is ticked. Tick it for them, or, if every email on your
provider is trusted, set `OPENID_REQUIRE_VERIFIED_EMAIL=False`.

`OPENID_ALLOW_ACCESS_TOKEN=True` lets an authenticating reverse proxy hand Taiga
an access token in the login URL (`/login?access_token=…`) instead of the usual
code flow. The token is only checked by calling the userinfo endpoint, which
accepts tokens issued to any client of the provider, and the link carries no
`state`: whoever gets a user to open such a link signs that user in to the
token's account. Enable it only behind a proxy that controls the login URL.

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

### Redirect URI

The button sends the page it is on as the redirect URI: `/login`, `/register`
or `/invitation/<token>` under your Taiga URL (and `TAIGA_SUBPATH`). Allow
`https://<your-taiga>/*` on the provider. A provider that only takes exact URIs
needs `https://<your-taiga>/login` and `https://<your-taiga>/register`; signing
in from an invitation link then fails there, so invited users sign in from the
login page and open the invitation again.

### Keycloak

Create a confidential OpenID Connect client (client authentication on, standard
flow) with the redirect URI `https://<your-taiga>/*`. To filter by group, add a
"Group Membership" mapper to the client with the token claim name `groups`,
"Full group path" off and "Add to userinfo" on, then set
`OPENID_FILTER_FIELD=groups` and `OPENID_FILTER=<group>`.

[`e2e/compose.yaml`](e2e/compose.yaml) is a complete, tested setup with Keycloak
([`e2e/keycloak/realm-taiga.json`](e2e/keycloak/realm-taiga.json)), based on
[taiga-docker](https://github.com/taigaio/taiga-docker).

### Other providers

Only Keycloak is covered by the end-to-end test. Notes for others:

- **Microsoft Entra ID**: authorization and token endpoints
  `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/authorize` and
  `.../token`, userinfo `https://graph.microsoft.com/oidc/userinfo`, scope
  `openid email profile`. Redirect URIs must be exact (see above). The userinfo
  has no `preferred_username` (the email becomes the username), no groups (the
  group filter cannot be used) and no `email_verified`, so linking to existing
  accounts is refused unless `OPENID_REQUIRE_VERIFIED_EMAIL=False`. Entra does
  not verify the `email` claim, so only turn it off for a single-tenant app
  whose users cannot change their email.
- **authentik**: endpoints `https://<authentik>/application/o/authorize/`,
  `.../token/` and `.../userinfo/`, with the trailing slash (see
  [Troubleshooting](#troubleshooting)). A regex redirect URI such as
  `https://taiga\.example\.com/.*` matches every page. The default `profile`
  scope sends `groups`, usable with `OPENID_FILTER_FIELD=groups`.

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

## Troubleshooting

- **"Our Oompa Loompas have not been able to get your credentials from
  OpenID."** The front shows this when the back's error has no message for
  users: the details are in the response to `POST /api/v1/auth` (browser
  developer tools: `status_code` and `error` from the provider) and in the
  taiga-back logs.
- **`status_code` 405 from the token endpoint**: `OPENID_TOKEN_URL` redirects
  (`http` to `https`, a missing trailing slash) and the redirect turns the POST
  into a GET. Use the exact URL from the provider's discovery document
  (`/.well-known/openid-configuration`).
- **"invalid login type"**: the back does not have the plugin. `ENABLE_OPENID`
  must be exactly `True` on taiga-back and taiga-async (exactly `true` on
  taiga-front), and taiga-async must run the back image too.
- **Provider behind a private CA** (`error`: "could not be reached
  (SSLError)", "certificate verify failed" in the logs): the back calls the token and userinfo endpoints itself. Mount a CA bundle
  holding the public CAs plus yours (e.g. the system bundle with your CA
  appended) on taiga-back and taiga-async and point `REQUESTS_CA_BUNDLE` at it.
- **`error`: "the identity provider did not answer within 10 s"** (or "could
  not be reached"): taiga-back cannot reach the provider (no egress, firewall,
  DNS); the logs name the endpoint. `OPENID_TIMEOUT` raises the limit if the
  provider is just slow.

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
