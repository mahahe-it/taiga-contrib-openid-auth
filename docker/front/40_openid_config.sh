#!/bin/sh
# Runs after taiga-front's 30_config_env_subst.sh: when it generated conf.json
# on this start and ENABLE_OPENID=true, add the OpenID settings and the plugin.
set -eu

conf=/usr/share/nginx/html/conf.json
marker=/tmp/openid-conf-generated

[ -f "$marker" ] || exit 0
rm -f "$marker"
[ "${ENABLE_OPENID:-false}" = "true" ] || exit 0

tmp=$(mktemp)
jq \
    --arg auth "${OPENID_URL:-}" \
    --arg clientId "${OPENID_CLIENT_ID:-}" \
    --arg name "${OPENID_NAME:-OpenID}" \
    --arg scope "${OPENID_SCOPE:-openid email}" \
    --arg plugin "plugins/openid-auth/openid-auth.json" \
    '.openidAuth = $auth
     | .openidClientId = $clientId
     | .openidName = $name
     | .openidScope = $scope
     | .contribPlugins = ((.contribPlugins // []) | if any(.[]; . == $plugin) then . else . + [$plugin] end)' \
    "$conf" > "$tmp"
cat "$tmp" > "$conf"
rm -f "$tmp"
echo "openid-auth: added to $conf"
