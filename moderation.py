# List of inappropriate words categorized by type
FORBIDDEN_WORDS = {

    # Inappropriate words related to 'hate' 
        "hate", "nazi", "nigga", "nigger", "kike", "paki", "gook", "spic", "wop", "chink", "darkie", "heeb", "jap", 
        "spick", "coon", "faggot", "dyke", "lesbo", "queer", "fag", "faggot", "fagot", "fagget",

    # Inappropriate words related to 'hate/threatening' 
        "kill", "murder", "lynch", "massacre", "snipe", "sniper", "terrorist", "rape", "rapist", 
        "assassinate", "assassin", "assassination", "assassin's",

    # Inappropriate words related to 'harassment' 
        "harassment", "bitch", "slut", "whore", "bastard", "asshole", "dickhead", "cunt", "prick", "pussy", "fag", "fatass", 
        "douchebag", "retard", "twat", "skank", "scumbag", "jackass", "dick", "shithead", "motherfucker", 
        "buttfucker", "cocksucker", "fuckhead", "pissflaps",

    # Inappropriate words related to 'harassament/threatening' 
        "beat", "choke", "stab", "burn", "shoot", "blow up", "fight", "destroy", "cut", "explode", "drown",

    # Inappropriate words related to 'self-harm' 
        "kill", "murder", "lynch", "massacre", "snipe", "suicide", "self-harm", "self-hate", "kill myself", "cutting", 
        "self-injury", "starve", "anorexia", "bulimia",

    # Inappropriate words related to 'self-harm/intent' 
        "I want to die", "I'm going to kill myself", "I want to cut", "I will cut myself", "I want to starve",

    # Inappropriate words related to 'self-harm/instructions' 
        "how to kill yourself", "how to commit suicide", "how to cut", "how to self-harm", "how to starve",

    # Inappropriate words related to 'sexual' 
        "sex", "sexual", "fuck", "fucker", "fucking", "dildo", "blowjob", "boob", "clitoris", "cock", "condom", 
        "cum", "cumming", "ejaculate", "erotic", "fellatio", "fetish", "horny", "masturbate", "orgasm", "penis", 
        "porn", "pornography", "prostitute", "pussy", "semen", "titty", "vagina",

    # Inappropriate words related to 'sexual/minors' 
        "child porn", "child pornography", "child sex", "underage sex", "underage porn", "minor sex",
 
    # Inappropriate words related to 'violence' 
        "kill", "murder", "violence", "abduct", "abduction", "assault", "behead", "blood", "bomb", "bomber", 
        "bombing", "brutal", "brutality", "choke", "crime", "criminal", "cut", "death", "decapitate", "destruct", 
        "destruction", "die", "drown", "explosive", "extort", "extortion", "fatal", "fight", "firearm", "grave", 
        "grieve", "gun", "hang", "homicide", "hostage", "hurt", "injure", "injury", "kidnap", "killing", "knife", 
        "lynch", "massacre", "massshooting", "molest", "molestation", "mutilate", "murderer", "overdose", 
        "poison", "rape", "rapist", "razor", "riot", "robbery", "sadism", "sadist", "shoot", "shooter", "shooting", 
        "slash", "slaughter", "snipe", "sniper", "stab", "stabbing", "strangle", "suicidal", "suffocate", 
        "terror", "terrorism", "terrorist", "torture", "tragic", "tragedy", "violent", "weapon",

    # Inappropriate words related to 'violence/graphic' 
        "decapitate", "behead", "stab", "cut", "bleed", "bloody", "gore", "mutilate", "slaughter"

}

def contains_forbidden_words(text):

    """
    Check if the given text contains any forbidden words.

    Parameters:
    text (str): The text to check.

    Returns:
    bool: True if the text contains forbidden words, False otherwise.
    """

    words = text.lower().split()
    for word in words:
        if word in FORBIDDEN_WORDS:
            return True
    return False
