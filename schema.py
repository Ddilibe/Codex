import graphene
from account.views import AccountMutation, AccountQuery
from genre.views import GenreQuery, GenreMutation
from books.views import BookMutation, BookQuery

class Query(
    BookQuery,
    GenreQuery,
    AccountQuery,
    graphene.ObjectType
    ):
    """
    The GraphQL Query class that defines all the available queries in the schema.

    This class extends from graphene.ObjectType and includes queries from the
    BookQuery, GenreQuery, and AccountQuery classes.

    Attributes:
        BookQuery: The class handling GraphQL queries related to books.
        GenreQuery: The class handling GraphQL queries related to genres.
        AccountQuery: The class handling GraphQL queries related to user accounts.
    """
    pass

class Mutations(
    BookMutation,
    GenreMutation,
    AccountMutation,
    graphene.ObjectType
    ):
    """
    The GraphQL Mutations class that defines all the available mutations in the schema.

    This class extends from graphene.ObjectType and includes mutations from the
    BookMutation, GenreMutation, and AccountMutation classes.

    Attributes:
        BookMutation: The class handling GraphQL mutations related to books.
        GenreMutation: The class handling GraphQL mutations related to genres.
        AccountMutation: The class handling GraphQL mutations related to user accounts.
    """
    pass

schema = graphene.Schema(query=Query, mutation=Mutations)
"""
The GraphQL Schema representing the entire API.

This schema includes queries and mutations from the Query and Mutations classes,
respectively. It acts as the entry point for executing GraphQL operations.

Attributes:
    query: An instance of the Query class, providing access to GraphQL queries.
    mutation: An instance of the Mutations class, providing access to GraphQL mutations.
"""
# authschema = graphene.Schema()
