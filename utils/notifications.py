from models_app.models import Notification

def creer_notification(destinataire, type_notif, message, lien=''):
    """
    Crée une notification pour un utilisateur.
    Appeler cette fonction depuis les vues engagement.
    """
    if destinataire:
        Notification.objects.create(
            destinataire = destinataire,
            type_notif   = type_notif,
            message      = message,
            lien         = lien,
        )
