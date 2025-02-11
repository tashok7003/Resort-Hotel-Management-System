from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
import csv
import xlsxwriter
from io import BytesIO
from reportlab.pdfgen import canvas
from .models import AnalyticsReport, DashboardWidget
from .forms import DateRangeForm, DashboardWidgetForm, ExportReportForm

@method_decorator(login_required, name='dispatch')
class AnalyticsDashboardView(ListView):
    model = DashboardWidget
    template_name = 'analytics/dashboard.html'
    context_object_name = 'widgets'
    
    def get_queryset(self):
        return DashboardWidget.objects.filter(is_visible=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_range_form'] = DateRangeForm()
        
        # Get quick stats for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        context['quick_stats'] = {
            'revenue': self.get_revenue_stats(thirty_days_ago),
            'occupancy': self.get_occupancy_stats(thirty_days_ago),
            'bookings': self.get_booking_stats(thirty_days_ago)
        }
        return context
    
    def get_revenue_stats(self, start_date):
        return AnalyticsReport.generate_revenue_report(
            start_date=start_date,
            end_date=timezone.now()
        ).data
    
    def get_occupancy_stats(self, start_date):
        return AnalyticsReport.generate_occupancy_report(
            start_date=start_date,
            end_date=timezone.now()
        ).data
    
    def get_booking_stats(self, start_date):
        return AnalyticsReport.generate_performance_report(
            start_date=start_date,
            end_date=timezone.now()
        ).data

@login_required
def generate_report(request):
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            report_type = request.POST.get('report_type')
            if report_type == 'REVENUE':
                report = AnalyticsReport.generate_revenue_report(start_date, end_date)
            elif report_type == 'OCCUPANCY':
                report = AnalyticsReport.generate_occupancy_report(start_date, end_date)
            else:
                report = AnalyticsReport.generate_performance_report(start_date, end_date)
            
            return render(request, 'analytics/report_detail.html', {
                'report': report
            })
    return redirect('analytics:dashboard')

@login_required
def export_report(request):
    if request.method == 'POST':
        form = ExportReportForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data['report_type']
            export_format = form.cleaned_data['format']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Generate report data
            if report_type == 'REVENUE':
                report = AnalyticsReport.generate_revenue_report(start_date, end_date)
            elif report_type == 'OCCUPANCY':
                report = AnalyticsReport.generate_occupancy_report(start_date, end_date)
            else:
                report = AnalyticsReport.generate_performance_report(start_date, end_date)
            
            # Export based on format
            if export_format == 'CSV':
                return export_csv(report)
            elif export_format == 'EXCEL':
                return export_excel(report)
            else:
                return export_pdf(report)
    return redirect('analytics:dashboard')

def export_csv(report):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.report_type.lower()}_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Report Type', report.report_type])
    writer.writerow(['Period', f'{report.start_date} to {report.end_date}'])
    writer.writerow([])
    
    # Write data based on report type
    if report.report_type == 'REVENUE':
        writer.writerow(['Total Revenue', report.data['total_revenue']])
        writer.writerow([])
        writer.writerow(['Revenue by Room Type'])
        writer.writerow(['Room Type', 'Revenue', 'Bookings'])
        for item in report.data['revenue_by_room_type']:
            writer.writerow([
                item['room_type__type'],
                item['total'],
                item['count']
            ])
    
    return response

def export_excel(report):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add formatting
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14
    })
    
    # Write report data
    worksheet.write('A1', f'{report.report_type} Report', title_format)
    worksheet.write('A2', f'Period: {report.start_date} to {report.end_date}')
    
    # Write specific report data
    if report.report_type == 'REVENUE':
        worksheet.write('A4', 'Total Revenue')
        worksheet.write('B4', report.data['total_revenue'])
        
        worksheet.write('A6', 'Revenue by Room Type', title_format)
        worksheet.write('A7', 'Room Type')
        worksheet.write('B7', 'Revenue')
        worksheet.write('C7', 'Bookings')
        
        row = 8
        for item in report.data['revenue_by_room_type']:
            worksheet.write(f'A{row}', item['room_type__type'])
            worksheet.write(f'B{row}', item['total'])
            worksheet.write(f'C{row}', item['count'])
            row += 1
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{report.report_type.lower()}_report.xlsx"'
    return response

def export_pdf(report):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report.report_type.lower()}_report.pdf"'
    
    # Create PDF
    p = canvas.Canvas(response)
    p.drawString(100, 800, f'{report.report_type} Report')
    p.drawString(100, 780, f'Period: {report.start_date} to {report.end_date}')
    
    # Add report-specific content
    if report.report_type == 'REVENUE':
        p.drawString(100, 740, f'Total Revenue: ${report.data["total_revenue"]}')
        
        y = 700
        p.drawString(100, y, 'Revenue by Room Type')
        y -= 20
        for item in report.data['revenue_by_room_type']:
            p.drawString(100, y, f'{item["room_type__type"]}: ${item["total"]} ({item["count"]} bookings)')
            y -= 20
    
    p.showPage()
    p.save()
    return response

@login_required
def widget_settings(request, pk):
    widget = DashboardWidget.objects.get(pk=pk)
    if request.method == 'POST':
        form = DashboardWidgetForm(request.POST, instance=widget)
        if form.is_valid():
            form.save()
            return redirect('analytics:dashboard')
    else:
        form = DashboardWidgetForm(instance=widget)
    
    return render(request, 'analytics/widget_settings.html', {
        'form': form,
        'widget': widget
    })

@login_required
def update_widget_position(request):
    if request.method == 'POST':
        widget_id = request.POST.get('widget_id')
        new_position = request.POST.get('position')
        
        widget = DashboardWidget.objects.get(id=widget_id)
        widget.position = new_position
        widget.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
