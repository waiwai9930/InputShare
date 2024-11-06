from dataclasses import dataclass
from notifypy import Notify

from ui import ICON_PNG_PATH
from utils.i18n import I18N

global_notification = Notify(
    default_application_name=I18N(["InputShare", "输入流转"]),
    default_notification_icon=str(ICON_PNG_PATH),
)

@dataclass
class Notification:
    title: str
    message: str

def send_notification(notification: Notification | None):
    if notification is None: return

    global_notification.title = notification.title
    global_notification.message = notification.message
    global_notification.send(block=False)
