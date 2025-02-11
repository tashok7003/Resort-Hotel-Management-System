from django import forms
from .models import Supplier, SupplierOrder, InventoryItem, InventoryTransaction, LeaveRequest, ShiftSwapRequest, OvertimeRecord, PerformanceMetric, PerformanceReview, RoomServiceRequest, RoomServiceFeedback

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        exclude = ['performance_score', 'active', 'last_order_date', 
                  'total_orders', 'on_time_delivery_rate', 'quality_rating']
        widgets = {
            'payment_terms': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class SupplierOrderForm(forms.ModelForm):
    class Meta:
        model = SupplierOrder
        fields = ['supplier', 'expected_delivery', 'total_amount']
        widgets = {
            'expected_delivery': forms.DateInput(attrs={'type': 'date'})
        }

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'category', 'minimum_stock', 'reorder_point', 
                 'unit_price', 'supplier', 'barcode', 'location']

class InventoryTransactionForm(forms.ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = ['transaction_type', 'quantity', 'reference_number', 'notes']

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ShiftSwapRequestForm(forms.ModelForm):
    class Meta:
        model = ShiftSwapRequest
        fields = ['requested_shift', 'reason']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['requested_shift'].queryset = Shift.objects.exclude(
                staff=user.staffprofile
            )

class OvertimeRecordForm(forms.ModelForm):
    class Meta:
        model = OvertimeRecord
        fields = ['date', 'hours', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class PerformanceMetricForm(forms.ModelForm):
    class Meta:
        model = PerformanceMetric
        fields = ['metric_type', 'value', 'date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['rating', 'comments', 'goals_set', 'next_review_date']
        widgets = {
            'next_review_date': forms.DateInput(attrs={'type': 'date'}),
        }

class RoomServiceRequestForm(forms.ModelForm):
    class Meta:
        model = RoomServiceRequest
        fields = ['service_type', 'description', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class RoomServiceAssignmentForm(forms.ModelForm):
    class Meta:
        model = RoomServiceRequest
        fields = ['assigned_to', 'estimated_duration']
        widgets = {
            'estimated_duration': forms.TextInput(attrs={'placeholder': 'HH:MM:SS'})
        }

class RoomServiceFeedbackForm(forms.ModelForm):
    class Meta:
        model = RoomServiceFeedback
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class RoomServiceStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=RoomServiceRequest.STATUS_CHOICES)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False) 