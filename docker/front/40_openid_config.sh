#!/bin/sh
# Runs after taiga-front's 30_config_env_subst.sh: when it generated conf.json
# on this start and ENABLE_OPENID=true, add the OpenID settings and the plugin.
# The marker goes only once that worked, so a failed start is retried.
set -eu

conf=/usr/share/nginx/html/conf.json
marker=/tmp/openid-conf-generated

[ -f "$marker" ] || exit 0
if [ "${ENABLE_OPENID:-false}" != "true" ]; then
    rm -f "$marker"
    exit 0
fi

warn_empty() {
    echo "openid-auth: warning: ENABLE_OPENID=true but $1 is empty: the OpenID button will not work" >&2
}
[ -n "${OPENID_URL:-}" ] || warn_empty OPENID_URL
[ -n "${OPENID_CLIENT_ID:-}" ] || warn_empty OPENID_CLIENT_ID

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
rm -f "$tmp" "$marker"
echo "openid-auth: added to $conf"
