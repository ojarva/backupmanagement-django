from django import forms

class DeleteForm(forms.Form):
    """ Form for confirming deleting disk """
    confirm = forms.BooleanField(required=True)

class AddForm(forms.Form):
    """ Form for confirming adding space """
    confirm = forms.BooleanField(required=True)
