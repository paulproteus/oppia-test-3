PLATFORM = "GAE"  # or django

if PLATFORM == "GAE":
    from gae_settings import *
else:
    from django_settings import *
