"""Custom Strawberry GraphQL View with SimpleJWT authentication and CSRF exemption."""
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from strawberry.django.views import GraphQLView
from rest_framework_simplejwt.authentication import JWTAuthentication


@method_decorator(csrf_exempt, name='dispatch')
class AuthenticatedGraphQLView(GraphQLView):
    """
    Subclassed GraphQLView that parses Authorization: Bearer <token>,
    sets request.user accordingly, and exempts CSRF for API clients.
    """

    def get_context(self, request, response):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            try:
                auth = JWTAuthentication()
                auth_result = auth.authenticate(request)
                if auth_result is not None:
                    user, token = auth_result
                    request.user = user
            except Exception:
                pass

        return super().get_context(request, response)
