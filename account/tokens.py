from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import logout
from datetime import datetime, timedelta
from graphql import GraphQLError
import six

class ExpiringTokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator for expiring tokens.

    This class extends the PasswordResetTokenGenerator provided by Django
    to include an expiration mechanism for the generated tokens.

    Attributes:
        None

    Methods:
        _make_hash_value(self, user, timestamp): Generates a hash value for the token.
    """
    def _make_hash_value(self, user, timestamp):
        """
        Generate a hash value for the token.

        Args:
            user (CustomUser): The user for whom the token is generated.
            timestamp (datetime): The timestamp indicating when the token is generated.

        Returns:
            str: The hash value based on user information and timestamp.
        """
        timestamp = datetime.now() + timedelta(seconds=10)
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )

token_generator = ExpiringTokenGenerator()

def verify_header(request):
    """
    Verify the authorization header and return the user.

    This function checks the authorization header in the request and
    verifies the user based on the token. If the token is valid, it returns
    the user; otherwise, it logs out the user, invalidates the token,
    and raises a GraphQLError.

    Args:
        request: The HTTP request object.

    Returns:
        CustomUser: The user associated with the valid token.

    Raises:
        GraphQLError: If the token is invalid or has expired.
    """
    from account.models import CustomUser

    if token := request.META.get('HTTP_AUTHORIZATION'):
        try:
            user = CustomUser.objects.get(token=token)
        except CustomUser.DoesNotExist:
            raise GraphQLError("Authorization Token is Invalid")

        if new_token := token_generator.check_token(user, token):
            return user
        else:
            logout(request)
            user.token = None
            user.save()
            raise GraphQLError("Token has Expired")

    raise GraphQLError("User has not Login")
