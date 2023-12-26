from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from account.tokens import verify_header
from django.shortcuts import render
from graphql import GraphQLError
from genre.models import Genre
import graphene


class GenreType(DjangoObjectType):
    """
    GraphQL type representing a Genre.

    Fields:
        genreid (str): The unique identifier for the genre.
        name (str): The name of the genre.
        description (str): The description of the genre.
    """
    class Meta:
        model = Genre
        fields = ('genreid', 'name', 'description')


class GenreNode(DjangoObjectType):
    """
    GraphQL Node representing a Genre for connection fields.

    Filter Fields:
        name (str): Filter by name (exact, icontains, istartswith).
        description (str): Filter by description (exact, icontains, istartswith, iendswith).
    """
    class Meta:
        model = Genre
        filter_fields = {
            "name": ['exact', 'icontains', 'istartswith'],
            "description": ["exact", "icontains", "istartswith", "iendswith"],
        }
        interfaces = (graphene.relay.Node,)


class CreateGenreMutation(graphene.Mutation):
    """
    Mutation to create a new Genre.

    Arguments:
        name (str): The name of the new genre (required).
        description (str): The description of the new genre (required).

    Returns:
        genre (GenreType): The created genre.
    """
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)

    genre = graphene.Field(GenreType)

    def mutate(self, info, name, description):
        try:
            user = verify_header(info.context)
            new_genre = Genre.objects.create(
                name=name, description=description
            )
            return CreateGenreMutation()
        except Exception as e:
            raise GraphQLError(str(e))


class EditGenreMutation(graphene.Mutation):
    """
    Mutation to edit an existing Genre.

    Arguments:
        genreid (str): The genre's unique identifier (required).
        name (str): The new name for the genre.
        description (str): The new description for the genre.

    Returns:
        genre (GenreType): The edited genre.
    """
    class Arguments:
        genreid = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()

    genre = graphene.Field(GenreType)

    def mutate(self, info, name, description, genreid):
        try:
            user = verify_header(info.context)
            oldgenre = Genre.objects.get(genreid=genreid)
            oldgenre.name = name if name is not None else oldgenre.name
            oldgenre.description = description if description is not None else oldgenre.description
            oldgenre.save()
            return EditGenreMutation(genre=oldgenre)
        except Exception as e:
            raise GraphQLError(str(e))


class DeleteGenreMutation(graphene.Mutation):
    """
    Mutation to delete an existing Genre.

    Arguments:
        genreid (str): The genre's unique identifier (required).

    Returns:
        message (JSONString): A message indicating the success of the deletion.
    """
    genre = graphene.Field(GenreType)

    class Arguments:
        genreid = graphene.String(required=True)

    def mutate(self, info, genreid):
        try:
            user = verify_header(info.context)
            oldgenre = Genre.objects.get(genreid=genreid)
            oldgenre.delete()
            return graphene.JSONString({"Genre": "Delete Successful"})
        except Exception as e:
            raise GraphQLError(str(e))


class GenreQuery(graphene.ObjectType):
    """
    GraphQL Query for retrieving genres.

    Fields:
        single_genre (list): Retrieve a single genre by genreid.
        all_genre (GenreNode): Retrieve all genres.
        all_genre_node (DjangoFilterConnectionField): Retrieve all genres with filtering.

    Methods:
        resolve_single_genre: Resolve the query for a single genre.
    """
    single_genre = graphene.List(GenreType)

    all_genre = graphene.relay.Node.Field(GenreNode)
    all_genre_node = DjangoFilterConnectionField(GenreNode)

    def resolve_single_genre(self, info, genreid):
        return Genre.objects.get(genreid=genreid)


class GenreMutation(graphene.ObjectType):
    """
    GraphQL Mutation for genre-related operations.

    Fields:
        creategenre (CreateGenreMutation): Mutation for creating a new genre.
        editgenre (EditGenreMutation): Mutation for editing an existing genre.
        deletegenre (DeleteGenreMutation): Mutation for deleting an existing genre.
    """
    creategenre = CreateGenreMutation.Field()
    editgenre = EditGenreMutation.Field()
    deletegenre = DeleteGenreMutation.Field()
