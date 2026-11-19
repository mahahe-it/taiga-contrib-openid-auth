#!/bin/sh
# Runs before taiga-front's 30_config_env_subst.sh, which writes conf.json only
# when it does not exist yet. Remember whether it is about to do that, so
# 40_openid_config.sh extends a generated conf.json and never a mounted one.
set -eu

if [ ! -f /usr/share/nginx/html/conf.json ]; then
    touch /tmp/openid-conf-generated
fi
