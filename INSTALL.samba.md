Samba installation
==================

We use standard Samba (3.4.7) setup.

Relevant part from shares configuration (*/etc/samba/smb.conf*):

```
[homes]
preexec = echo \"%u connected to %S from %m (%I)\" >> /var/log/samba/log.connect
postexec = echo \"%u disconnected from %S from %m (%I)\" >> /var/log/samba/log.disconnect
comment = Userbackup directories (U:)
valid users = %S
browseable = no
writable = yes
inherit acls = yes
path = /srv/userbackup/%S
```
