AFP installation and configuration
==================================

Original version written by Vesa Alho <vesa.alho@futurice.com>


Installation and configuration on Ubuntu 10.04 Lucid
----------------------------------------------------

The latest netatalk is not available as a proper deb package. It must be compiled manually.

* Download the latest netatalk, at least 2.2.4 works with Lion, Snow Leopard and Leopard. Extract.
* Install needed software for compile

```
aptitude install devscripts cracklib2-dev dpkg-dev libssl-dev
apt-get build-dep netatalk
```

* Install netatalk from Ubuntu repo to get depencies.

```
apt-get install netatalk
apt-get remove netatalk
```

Good idea is to run "*apt-get install*" for every dependency. Otherwise "*apt-get autoremove*" will delete those later on.

* Compile and install netatalk

```
./configure --with-ssl --enable-debian --with-cracklib
make install
```

* Prepare netatalk

```
rm -fr /etc/netatalk
ln -s /usr/local/etc/netatalk /etc/netatalk
cp /usr/src/netatalk-2.1.4/distrib/initscripts/netatalk /etc/init.d/netatalk
chmod 755 /etc/init.d/netatalk
update-rc.d netatalk defaults
```

* Edit configuration /etc/default/netatalk

```
ATALK_NAME="<hostname>"
ATALK_MAC_CHARSET='MAC_ROMAN'
ATALK_UNIX_CHARSET='LOCALE'
AFPD_MAX_CLIENTS=300
AFPD_UAMLIST="-U uams_dhx.so,uams_dhx2.so"
AFPD_GUEST=nobody
ATALKD_RUN=no
PAPD_RUN=no
CNID_METAD_RUN=yes
AFPD_RUN=yes
TIMELORD_RUN=no
A2BOOT_RUN=no
ATALK_BGROUND=no
export ATALK_MAC_CHARSET
export ATALK_UNIX_CHARSET
```

*/etc/netatalk/afpd.conf*:

```
- -transall -uamlist uams_dhx.so,uams_dhx2.so
```

* Edit share configuration */etc/netatalk/AppleVolumes.default*

```
# The line below sets some DEFAULT, starting with Netatalk 2.1.
:DEFAULT: options:usedots,upriv
# following default used in userbackuo
# :DEFAULT: cnidscheme:dbd ea:sys options:usedots,upriv
#
/srv/userbackup/$u "$u" options:usedots options:upriv umask:7077 options:tm
# End of File
```

* Install Avahi (used to advertise AFP service for Mac clients)

```
sudo apt-get install avahi-daemon libnss-mdns
```

Edit */etc/nsswitch.conf*. Just add *mdns* at the end of the line that starts with *hosts:*. Now the line should look like this:

```
hosts: files mdns4_minimal [NOTFOUND=return] dns mdns4 mdns
```

*/etc/avahi/services/afpd.service* (remember to use your own MAC address):

```
<?xml version="1.0" standalone='no'?><!--*-nxml-*-->
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
<name replace-wildcards="yes">userbackup</name>
<service>
 <type>_afpovertcp._tcp</type>
 <port>548</port>
</service>
<service>
 <type>_device-info._tcp</type>
 <port>0</port>
 <txt-record>model=Xserve</txt-record>
</service>
<service>
 <type>_adisk._tcp</type>
 <port>9</port>
 <txt-record>sys=waMA=52:54:00:40:3f:1d,adVF=0x100</txt-record>
 <txt-record>dk0=adVF=0x83,adVN=Time Machine</txt-record>
</service>
</service-group>
```

* Start services

```
/etc/init.d/netatalk restart
/etc/init.d/avahi restart
```

* Test using a Mac OS X client. New icon should appear on Finder sidebar
