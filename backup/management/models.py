from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    """ Extension to built-in User model. """
    user = models.OneToOneField(User)
    max_space = models.IntegerField(default=300, verbose_name="Maximum space (GB)")
    def __unicode__(self):
        return "Profile: %s" % self.user


def create_user_profile(sender, instance, created, **kwargs):
    """ Automatically create user profile if user is created """
    if created:
        UserProfile.objects.create(user=instance)

# Register trigger
post_save.connect(create_user_profile, sender=User)
