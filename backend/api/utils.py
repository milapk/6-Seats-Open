from rest_framework_simplejwt.tokens import RefreshToken

def get_jwt_tokens(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)
    