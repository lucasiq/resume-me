# coding=utf-8
# Utility Functions

def get_message_text(message):
    messages = {
        "review_saved" : "Votre critique a été enregistré. Merci.",
        "sorry_old_model" : "Désolé, votre critique n’a pas pu être soumise.  "
                            "Il y a actuellement un problème avec notre base de données que nous sommes en train de résoudre.",
        "thank_volunteer" : "Merci d’avoir envoyer un e-mail d’encouragement à votre bénévole."
    }
    return(messages[message])

