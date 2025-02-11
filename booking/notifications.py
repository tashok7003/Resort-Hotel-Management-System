from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

class GroupBookingNotificationService:
    def __init__(self, group_booking):
        self.group_booking = group_booking
        
    def send_confirmation_email(self):
        """Send confirmation email to group leader"""
        context = {
            'booking': self.group_booking,
            'members': self.group_booking.groupmember_set.all(),
            'room_allocations': self.group_booking.grouproomallocation_set.all()
        }
        
        html_content = render_to_string('emails/group_booking_confirmation.html', context)
        text_content = render_to_string('emails/group_booking_confirmation.txt', context)
        
        msg = EmailMultiAlternatives(
            subject=f'Group Booking Confirmation - {self.group_booking.group_name}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.group_booking.group_leader.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
    def send_member_notifications(self):
        """Send individual notifications to group members"""
        for member in self.group_booking.groupmember_set.all():
            room_allocation = self.group_booking.grouproomallocation_set.get(member=member)
            context = {
                'member': member,
                'booking': self.group_booking,
                'room': room_allocation.room
            }
            
            html_content = render_to_string('emails/group_member_notification.html', context)
            text_content = render_to_string('emails/group_member_notification.txt', context)
            
            msg = EmailMultiAlternatives(
                subject=f'Your Group Booking Details - {self.group_booking.group_name}',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[member.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
    def send_payment_reminder(self):
        """Send payment reminder to group leader"""
        context = {
            'booking': self.group_booking,
            'remaining_amount': self.group_booking.get_remaining_payment()
        }
        
        html_content = render_to_string('emails/payment_reminder.html', context)
        text_content = render_to_string('emails/payment_reminder.txt', context)
        
        msg = EmailMultiAlternatives(
            subject=f'Payment Reminder - {self.group_booking.group_name}',
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.group_booking.group_leader.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send() 