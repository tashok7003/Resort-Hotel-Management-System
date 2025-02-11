from django import forms
from .models import GroupBooking, GroupMember

class GroupBookingForm(forms.ModelForm):
    class Meta:
        model = GroupBooking
        fields = ['group_name', 'group_size', 'group_type', 'special_requests']
        
    def clean_group_size(self):
        size = self.cleaned_data['group_size']
        if size < 5:
            raise forms.ValidationError("Group booking requires minimum 5 members")
        if size > 50:
            raise forms.ValidationError("Maximum group size is 50")
        return size

class GroupMemberForm(forms.ModelForm):
    class Meta:
        model = GroupMember
        fields = ['name', 'email', 'phone', 'special_requirements', 'room_preference']

GroupMemberFormSet = forms.inlineformset_factory(
    GroupBooking, GroupMember, form=GroupMemberForm,
    extra=1, can_delete=True, min_num=5, validate_min=True
) 