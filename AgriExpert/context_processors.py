# AgriExpert/context_processors.py
def agribot_context(request):
    return {
        'show_agribot': True,  # You can add conditions here if needed
    }