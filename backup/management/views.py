from decorators import *
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, condition, require_GET
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from forms import AddForm, DeleteForm
from disk import Disk, chpasswd
import os
import pickle
import subprocess
import traceback

@login_required
@require_GET
@staff_member_required
@render("adminview.html")
def adminview(request):
    """ Admin list view of users and disk usages """
    username = request.user.username
    users_list = []
    for userdetail in User.objects.all():
         disk = __get_diskinfo(userdetail.username)
         users_list.append((userdetail.username, disk))
    return {"users": users_list}

@login_required
@require_GET
@disk_required(reverse_lazy("create_storage"))
@render("index.html")
def indexview(request):
    """ Main page for user """
    username = request.user.username

    disk = Disk(username)
    disk.get_info()
    disk.get_waittime()
    ret_dict = {}
    if disk.mounted:
        try:
            backupinfo = disk.fetch_backups()
            ret_dict["backupinfo"] = backupinfo.get_backups()
        except:
            ret_dict["backup_stacktrace"] = traceback.format_exc()

    ret_dict["hostname"] = settings.HOSTNAME    
    ret_dict["disk"] = disk
    return ret_dict

@login_required
@disk_required(reverse_lazy("create_storage"))
@csrf_protect
@render("change_password.html")
def change_password(request):
    """ View for changing user password. Requires pwgen. Tries to change both unix password and samba password. """
    username = request.user.username

    arguments = {}
    if request.method == 'POST':
        p = subprocess.Popen(["pwgen", "10", "1"], stdout=subprocess.PIPE)
        password = p.communicate()[0].strip()
        if p.returncode is not 0:
            raise Exception("pwgen failed with status %s" % p.returncode)

        if not chpasswd(username, password):
            raise Exception("chpasswd failed")

        arguments["password"] = password
        arguments["changed"] = True

    return arguments


@login_required
@disk_required(reverse_lazy("create_storage"))
@csrf_protect
@json_render
def mount(request):
    """ Mount the disk. """
    def _mount_return(success, status):
        return {"success": success, "status": status, "key": "mount"}

    username = request.user.username
    disk = Disk(username)
    disk.get_info(username)
    if disk.mounted:
        return _mount_response(False, "disk is already mounted")
    arguments = {}
    if request.method == 'POST':
        if disk.mount():
            return _mount_return(True, "mount succeeded")
        return _mount_return(False, "mount failed")
    return _mount_return(False, "Invalid request")

@login_required
@disk_required(reverse_lazy("create_storage"))
@csrf_protect
@json_render
def fsck(request):
    """ Run fsck (filesystem check). btrfs do not include working fsck tool. ext4 do not support online fsck (yet). """

    def _fsck_return(success, status):
        return {"success": success, "status": status, "key": "fsck"}
    username = request.user.username
    disk = Disk(username)
    arguments = {}
    if request.method == 'POST':
         if disk.fsck():
             return _fsck_return(True, "fsck succeeded")
         return _fsck_return(False, "fsck failed: %s\n%s" % (p.returncode, output))
    return _fsck_return(False, "Invalid request")

@login_required
@disk_required(reverse_lazy("create_storage"))
@csrf_protect
@json_render
def defragment(request):
    """ Only btrfs requires/includes online defragment program """
    def _defragment_return(success, status):
        return {"success": success, "status": status, "key": "defragment"}
    username = request.user.username

    disk = Disk(username)
    if not disk.mounted:
        return _defragment_return(False, "disk is not mounted")
    arguments = {}
    if request.method == 'POST':
        if disk.defragment():
             return _defragment_return(True, "successfully defragmented")
        return _defragment_return(False, "btrfsctl failed\n%s" % output)
    return _defragment_return(False, "Invalid request")
         
@login_required
@disk_no_required(reverse_lazy("indexview"))
@csrf_protect
@render("create_storage.html")
def create_storage(request):
    """ Create user storage space and set up password """

    username = request.user.username
    disk = Disk(username)
    if request.method == 'POST':
        if disk.create_storage(settings.DEFAULT_DISK_SIZE):
            return HttpResponseRedirect(reverse_lazy("indexview"))
        raise Exception("Creation failed")
    return {"default_disk_size": settings.DEFAULT_DISK_SIZE, "default_add_space_amount": settings.DEFAULT_ADD_SPACE_AMOUNT}

@login_required
@disk_required(reverse_lazy("create_storage"))
@csrf_protect
@render("add_space.html")
def add_space(request):
    """ Add more space to user disk. TODO: progress indicator, as lvextend+resize2fs takes some time. """
    username = request.user.username
    disk = Disk(username)
    if not disk.mounted:
        raise Exception("Disk is not mounted")

    added = False
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            print form.cleaned_data
            if form.cleaned_data["confirm"] is True:
                disk.add_space(settings.DEFAULT_ADD_SPACE_AMOUNT)
                added = True
    else:
        form = AddForm()
    return {"form": form, "added": added}

@login_required
@disk_required(reverse_lazy("create_storage"))
@csrf_protect
@render("delete_disk.html")
def delete_disk(request):
    """ Handles deleting the disk """
    username = request.user.username
    disk = Disk(username)
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"] is True:
                if disk.delete_disk():
                    return HttpResponseRedirect(reverse_lazy("delete_disk_done"))
                return {"form": form, "umount_failed": True}
    else:
        form = DeleteForm()
    return {'form': form}

@login_required
@disk_no_required(reverse_lazy("indexview"))
@render("disk_deleted.html")
def delete_disk_done(request):
    """ Confirmation of disk deletion. Should be Class view """
    return {}


@login_required
@disk_required(reverse_lazy("create_storage"))
@csrf_protect
@render("delete_timemachine.html")
def delete_timemachine(request):
    """ Delete timemachine backups, if any """
    username = request.user.username
    disk = Disk(username)
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"] is True:
                if disk.delete_timemachine():
                    return HttpResponseRedirect(reverse_lazy("delete_timemachine_done"))
                return {"form": form, "delete_failed": True}
    else:
        form = DeleteForm()
    return {'form': form}

@login_required
@disk_required(reverse_lazy("create_storage"))
@render("timemachine_deleted.html")
def delete_timemachine_done(request):
    """ Confirmation of timemachine deletion. Should be Class view """
    return {}
 
@login_required
def userspace_image(request):
    """ Get current user's space usage image """
    username = request.user.username
    if not os.path.exists("%s/userspace/%s.png" % (settings.MEDIA_ROOT, username)):
        return Http404
    image_data = open("%s/userspace/%s.png" % (settings.MEDIA_ROOT, username), "rb").read()
    return HttpResponse(image_data, mimetype="image/png")
