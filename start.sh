#!/bin/bash

# set dns
# echo DNS=8.8.8.8  >> /etc/systemd/resolved.conf 
# systemctl restart systemd-resolved

# flush system font
fc-cache -fv > /dev/null

mkdir -p /app/knowledge_base/smb > /dev/null 2>&1

# start nginx meilisearch memcached smbd
service nginx start
/app/meilisearch --master-key rzHvvVSus8cu_jgZ1UuXB5SyfXAGeSUMIlITMov9uig --http-addr  0.0.0.0:7700 &
memcached -d -m 2 -l 127.0.0.1 -p 11211 -u nobody &
service smbd restart
service nmbd restart

cd /app
#导入默认
# python3 manage.py loaddata datadump.json
# cp  /app/lib/* /usr/local/lib/python3.10/dist-packages/extractous/
# start plugin
/app/cron/cron.sh &

# start smb handler
chmod +x /app/smb_handle/smbhandle
cd /app/smb_handle/ && ./smbhandle -p /app/knowledge_base/smb &

# start uwsgi
uwsgi --ini uwsgi.ini
tail -f /dev/null

