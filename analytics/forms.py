from django import forms
from .models import AnalyticsReport, DashboardWidget

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date must be after start date")
        return cleaned_data

class DashboardWidgetForm(forms.ModelForm):
    class Meta:
        model = DashboardWidget
        fields = ['name', 'widget_type', 'position', 'is_visible', 'settings']
        widgets = {
            'settings': forms.Textarea(attrs={
                'class': 'json-editor',
                'rows': 4,
                'placeholder': '{"key": "value"}'
            })
        }

    def clean_settings(self):
        """Validate that settings is valid JSON"""
        import json
        settings = self.cleaned_data.get('settings')
        try:
            if settings:
                json.loads(settings)
            return settings
        except ValueError:
            raise forms.ValidationError("Invalid JSON format")

class ExportReportForm(forms.Form):
    EXPORT_FORMATS = [
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV')
    ]
    
    report_type = forms.ChoiceField(choices=AnalyticsReport.REPORT_TYPES)
    format = forms.ChoiceField(choices=EXPORT_FORMATS)
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    ) 