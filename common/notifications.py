from common.models import NotificationLog

def send_notification(recipient_name, recipient_contact, notification_type, message, subject=None):
    """
    Sends a mock notification (prints to console and records the event in the database).
    """
    print(f"--- MOCK DISPATCH: Sending {notification_type.upper()} ---")
    if subject:
        print(f"Subject: {subject}")
    print(f"To: {recipient_name} ({recipient_contact})")
    print(f"Message: {message}")
    print("-------------------------------------------------")
    
    log = NotificationLog.objects.create(
        recipient_name=recipient_name,
        recipient_contact=recipient_contact,
        notification_type=notification_type,
        subject=subject,
        message=message,
        is_sent=True
    )
    return log
