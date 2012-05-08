What
====

This is backup management software used by Futurice. Basic idea is to 
empower employees to manage their own backup disks (virtual disks in 
LVM). System sets up separate user account and password for backups. 
Idea is to separate backups from normal user passwords.

Prerequisities
--------------

* Backup storage in LVM disk (/dev/backupdisks in our setup)
* ext4 (or btrfs, may not work. Futurice currently uses ext4)
* ACLs enabled (usually it's)
* Django installed (>= 1.3.1)
* Web server with authentication (Futurice uses single sign-on, but for 
  example basic auth is fine). Preferrably https as password is highly 
  confidential.
* Samba (for Windows backups, see also INSTALL.samba.txt)
* netatalk (for AFP support, see also INSTALL.afp.txt)
* rrdtool

Copy-paste for installing packages:

```
apt-get install e2fslibs e2fsprogs apache2 libapache2-mod-fastcgi python-flup samba rrdtool python-django
```

* netatalk installation
* samba configuration
* LVM configuration

Quick installation
------------------

1. Install prerequisities
1. add "backupmanagement" user
1. checkout code to /home/backupmanagement/
1. add sudoers entry (see below) and configure wrappers
1. Check values in backup/settings.py (at least LVM_ROOT and DIRECTORIES_ROOT)
1. In directory backup/ run "python manage.py check_prerequisities". Fix possible problems.
1. run "python manage.py syncdb"
1. run "python manage.py collectstatic"
1. start fastcgi server: "sudo -u backupmanagement -i; cd backup; ./bin/start.sh"
1. configure apache2
1. add crontab entries (see below)

Notes
-----

FastCGI is recommended (over WSGI), as it runs under different user. If you run with WSGI, you have to give sudo rights to web server user.

Crontab entries in our configuration
------------------------------------

This is optional. Add to backupmanagement user crontab:

```
sudo -u backupmanagement crontab -e
```

```
@reboot /home/backupmanagement/backup/bin/start.sh # starts fastcgi server on reboot.
* * * * * cd /home/backupmanagement/backup; python manage.py rrd_waittime
*/5 * * * * cd /home/backupmanagement/backup; python manage.py update_df_stats
```

Example apache configuration
----------------------------

* enable ssl
* enable whatever authentication, for example basic auth.

```
RewriteEngine on
FastCGIExternalServer /var/www/backup.fcgi -socket /home/backupmanagement/backup/backup.sock

RewriteRule ^/backup/static/(.*)$ /home/backupmanagement/backup/static/$1 [L]
RewriteRule ^/backup/(.*)$ /backup.fcgi/$1 [QSA,L]
```

Permissions configuration
-------------------------

IMPORTANT: If wrappers directory is under a directory owned by 
backupmanagement user, compromised account leads to total compromise of 
system. Steps to protect:

```
mkdir -p /opt/backupmanagement
cp -R /home/backupmanagement/wrappers /opt/backupmanagement/wrappers/
chown -R root:root /opt/backupmanagement 
chmod -R 700 /opt/backupmanagement/*
```

Add this to sudoers (*sudo visudo*):

```
backupmanagement ALL=NOPASSWD: /opt/backupmanagement/wrappers/chmod.py, /opt/backupmanagement/wrappers/chown.py, /opt/backupmanagement/wrappers/chpasswd.py, /opt/backupmanagement/wrappers/defragment-btrfs.py, /opt/backupmanagement/wrappers/deluser.py, /opt/backupmanagement/wrappers/df.py, /opt/backupmanagement/wrappers/dmsetup.py, /opt/backupmanagement/wrappers/fetch_backups.py, /opt/backupmanagement/wrappers/lvcreate.py, /opt/backupmanagement/wrappers/lvdisplay.py, /opt/backupmanagement/wrappers/lvextend.py, /opt/backupmanagement/wrappers/lvremove.py, /opt/backupmanagement/wrappers/mkdir.py, /opt/backupmanagement/wrappers/mkfs-ext4.py, /opt/backupmanagement/wrappers/mount.py, /opt/backupmanagement/wrappers/resize2fs.py, /opt/backupmanagement/wrappers/rmdir.py, /opt/backupmanagement/wrappers/rm-timemachine.py, /opt/backupmanagement/wrappers/setfacl.py, /opt/backupmanagement/wrappers/smbpasswd.py, /opt/backupmanagement/wrappers/umount.py, /opt/backupmanagement/wrappers/useradd.py
```

Also, check that *env_reset* is enabled in sudoers configuration (usually it's on by 
default).

All sudo commands go through python wrappers. That way backupmanagement 
user can only run specific commands with safe arguments. For example, 
compromised user can only delete backups, not random files from OS. It 
can't change root password or add new user with uid/gid 0 etc. 
Unfortunately, attacker with access to backupmanagement user can change 
other's passwords and access backup files. Preventing this while still 
allowing automatic configuration is not possible.

You may want to add administrators (basically everyone with additional
sudo rights) to wrappers/wrappers_settings.py file to prevent changes
to admin passwords and/or files.

TODO
----

Will do some day:
- better error handling (now just throws traceback to user)
- check that there's space on LVM volume
- tested btrfs support

Our setup
---------

All employees can create their own backup spaces. Our setup currently 
supports Windows backups over samba (unfortunately, Windows 7 complains 
that "Your files are not protected", no idea how to fix that) and Mac OS 
X Time Machine over AFP. For AFP instructions, check out 
INSTALL.afp.md. We had some difficulties with setting up AFP, and to 
get it working with Mac OS X Lion.

We use newest Ubuntu LTS (as a time of writing, 12.04). Our servers run 
on virtual machines under KVM. One of backup servers use disk rack 
connected to PCI-E RAID controller (RAID5 + hot spare), other one is 
Synology NAS device with RAID6 over iSCSI in separate network.
