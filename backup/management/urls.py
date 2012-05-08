from django.conf.urls.defaults import *
from views import indexview, create_storage, change_password, delete_disk, add_space,  delete_disk_done, fsck, mount, defragment, userspace_image, adminview, delete_timemachine, delete_timemachine_done

urlpatterns = patterns('',
    url(r'^create_storage$', create_storage, name="create_storage"),
    url(r'^change_password$', change_password, name="change_password"),
    url(r'^add_space$', add_space, name="add_space"),
    url(r'^delete_disk$', delete_disk, name="delete_disk"),
    url(r'^delete_disk_done$', delete_disk_done, name="delete_disk_done"),
    url(r'^delete_timemachine$', delete_timemachine, name="delete_timemachine"),
    url(r'^delete_timemachine_done$', delete_timemachine_done, name="delete_timemachine_done"),
    url(r'^$', indexview, name="indexview"),
    url(r'^adminview$', adminview, name="adminview"),
    url(r'^userspace_image$', userspace_image, name="userspace_image"),
    url(r'^api/fsck$', fsck, name="fsck"),
    url(r'^api/mount$', mount, name="mount"),
    url(r'^api/defragment$', defragment, name="defragment"),
)


