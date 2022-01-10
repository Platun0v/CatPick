set -e

printenv | grep -v "no_proxy" >> /etc/environment
export TZ="Europe/Moscow"
date
#. /opt/pysetup/.venv/bin/activate
cron
tail -f /var/log/cron.log
#
#exec "$@"