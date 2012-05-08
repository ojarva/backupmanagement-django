#!/bin/sh
#
# Add this file to crontab to start backupmanagement at boot:
# @reboot /home/backupmanagement/backup/bin/start.sh

PROJDIR=$HOME/backup
PIDFILE="$PROJDIR/backup.pid"
SOCKET="$PROJDIR/backup.sock"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

/usr/bin/env - \
  PYTHONPATH="../python:.." \
  python ./manage.py runfcgi --settings=backup.settings socket=$SOCKET pidfile=$PIDFILE workdir=$PROJDIR

chmod a+w $SOCKET

