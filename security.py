import config 
def current_user_id():
    """Return the user id of the current user, or None if not logged in."""
    return config.DEMO_USER_ID