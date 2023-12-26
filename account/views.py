from graphene_django.forms.mutation import DjangoModelFormMutation
from account.models import CustomUser, PatronUser, AuthorUser
from django.contrib.auth import authenticate, login, logout
from account.tokens import token_generator, verify_header
from graphene_django import DjangoObjectType
from django.shortcuts import render
from graphql import GraphQLError
import graphene

class CustomUserType(DjangoObjectType):
    """
    GraphQL type for CustomUser model.

    Fields:
    - email: Email address of the user.
    - username: User's username.
    - first_name: User's first name.
    - last_name: User's last name.
    - role: User's role.
    - token: User's authentication token.
    """
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'role', 'token')

class PatronUserType(DjangoObjectType):
    """
    GraphQL type for PatronUser model.

    Fields:
    - patronid: ID of the patron.
    - user: Related user.
    - address: Patron's address.
    - phone_number: Patron's phone number.
    - created_at: Timestamp of creation.
    - updated_at: Timestamp of last update.
    """
    class Meta:
        model = PatronUser
        fields = ("patronid", "user", "address", "phone_number", "created_at", "updated_at")

class AuthorUserType(DjangoObjectType):
    """
    GraphQL type for AuthorUser model.

    Fields:
    - author_id: ID of the author.
    - user: Related user.
    - birthdate: Author's birthdate.
    - nationality: Author's nationality.
    """
    class Meta:
        model = AuthorUser
        fields = ('author_id', "user", "birthdate", "nationality")

class UserType(DjangoObjectType):
    """
    GraphQL type for CustomUser model.

    Fields:
    - email: Email address of the user.
    - first_name: User's first name.
    - last_name: User's last name.
    - token: User's authentication token.
    """
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'token')

class LoginMutation(graphene.Mutation):
    """
    Mutation for user login.

    Arguments:
    - email: User's email address.
    - password: User's password.

    Returns:
    - user: The logged-in user.
    """
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, email, password):
        """
        Authenticate user and log in.

        Parameters:
        - info: GraphQL resolver info.
        - email: User's email address.
        - password: User's password.

        Returns:
        - LoginMutation object.
        """
        print("Authenticating user")
        if user := CustomUser.objects.get(email=email):
            if user.check_password(password):
                if not(user.token):
                    user.token = token_generator.make_token(user)
                user.save()
                login(info.context, user)
                return LoginMutation()
        raise GraphQLError("Invalid credentials. Please try again.")

class SignUpMutation(graphene.Mutation):
    """
    Mutation for user registration.

    Arguments:
    - email: User's email address.
    - username: User's username.
    - first_name: User's first name.
    - last_name: User's last name.
    - password: User's password.
    - confirm_password: Confirmation of user's password.

    Returns:
    - user: The registered user.
    """
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)
        
    user = graphene.Field(CustomUserType)

    def mutate(self, info, email, username, first_name, last_name, password, confirm_password):
        """
        Register a new user.

        Parameters:
        - info: GraphQL resolver info.
        - email: User's email address.
        - username: User's username.
        - first_name: User's first name.
        - last_name: User's last name.
        - password: User's password.
        - confirm_password: Confirmation of user's password.

        Returns:
        - SignUpMutation object.
        """
        if password == confirm_password:
            try:
                new_user = CustomUser.objects.create(
                    email=email, username=username, first_name=first_name,
                    last_name=last_name, password=password
                )
                return SignUpMutation()
            except Exception as e:
                raise GraphQLError(str(e))
        raise GraphQLError("Password does not match")

class LogOutMutation(graphene.Mutation):
    """
    Mutation for user logout.

    Returns:
    - user: The logged-out user.
    """
    user = graphene.Field(CustomUserType)

    def mutate(self, info):
        """
        Log out the user.

        Parameters:
        - info: GraphQL resolver info.

        Returns:
        - LogOutMutation object.
        """
        request = info.context
        try:
            user = verify_header(request)
            user.token = None
            user.save()
            logout(request)
            return LogOutMutation()
        except Exception as e:
            raise GraphQLError(str(e))

class BecomePatronMutation(graphene.Mutation):
    """
    Mutation for a user becoming a patron.

    Arguments:
    - address: Patron's address.
    - phone_number: Patron's phone number.

    Returns:
    - patron: The created patron user.
    """
    class Arguments:
        address = graphene.String(required=True)
        phone_number = graphene.String(required=True)

    patron = graphene.Field(PatronUserType)

    def mutate(self, info, address, phone_number):
        """
        Make the user a patron.

        Parameters:
        - info: GraphQL resolver info.
        - address: Patron's address.
        - phone_number: Patron's phone number.

        Returns:
        - BecomePatronMutation object.
        """
        user = verify_header(info.context)
        new_patron = PatronUser(
            address=address, phone_number=phone_number, user=user
        )
        user.is_patron = True
        user.save()
        new_patron.save()
        return BecomePatronMutation()

class BecomeAuthorMutation(graphene.Mutation):
    """
    Mutation for a user becoming an author.

    Arguments:
    - birthdate: Author's birthdate.
    - nationality: Author's nationality.

    Returns:
    - author: The created author user.
    """
    class Arguments:
        birthdate = graphene.String(required=True)
        nationality = graphene.String(required=True)

    author = graphene.Field(AuthorUserType)

    def mutate(self, info, birthdate, nationality):
        """
        Make the user an author.

        Parameters:
        - info: GraphQL resolver info.
        - birthdate: Author's birthdate.
        - nationality: Author's nationality.

        Returns:
        - BecomeAuthorMutation object.
        """
        user = verify_header(info.context)
        new_author = AuthorUser(
            birthdate=birthdate, nationality=nationality, user=user
        )
        user.is_author = True
        user.save()
        new_author.save()
        return BecomeAuthorMutation()

class AuthorQuery(graphene.ObjectType):
    """
    GraphQL query for author-related operations.

    Fields:
    - all_author: Retrieve all author users.
    """
    all_author = graphene.List(AuthorUserType)
    
    def resolve_all_author(self, info):
        """
        Resolver for retrieving all author users.

        Parameters:
        - info: GraphQL resolver info.

        Returns:
        - All author users.
        """
        return AuthorUser.objects.all()

class AccountMutation(graphene.ObjectType):
    """
    GraphQL mutation for account-related operations.

    Fields:
    - login: User login mutation.
    - signup: User signup mutation.
    - logout: User logout mutation.
    - becomeauthor: User become author mutation.
    - becomepatron: User become patron mutation.
    """
    login = LoginMutation.Field()
    signup = SignUpMutation.Field()
    logout = LogOutMutation.Field()
    becomeauthor = BecomeAuthorMutation.Field()
    becomepatron = BecomePatronMutation.Field()

class AccountQuery(
    AuthorQuery,
    graphene.ObjectType):
    """
    GraphQL query for account-related operations.
    Inherits AuthorQuery and ObjectType.

    No additional fields.
    """
    pass
