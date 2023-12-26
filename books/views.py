from books.models import Book, Transactions, BookStatus, Reviews
from graphene_django.filter import DjangoFilterConnectionField
from django.shortcuts import get_object_or_404
from graphene_django import DjangoObjectType
from account.tokens import verify_header
from account.models import AuthorUser
from django.shortcuts import render
from graphql import GraphQLError
import graphene

"""
GraphQL Mutations for Modifying Book Relationships

This module contains GraphQL mutations for adding and removing relationships, such as authors and genres, to/from a book.

Classes:
    - AddAuthorToBookMutation: Mutation for adding an author to a book.
    - AddGenreToBookMutation: Mutation for adding a genre to a book.
    - RemoveAuthorFromBookMutation: Mutation for removing an author from a book.
    - RemoveGenreFromBookMutation: Mutation for removing a genre from a book.

"""

class BookType(DjangoObjectType):
    """
    GraphQL Type for representing a Book.

    Attributes:
        bookid (Int): The unique identifier for the book.
        title (String): The title of the book.
        isbn (String): The International Standard Book Number.
        description (String): A brief description of the book.
        author (String): The author of the book.
        genres (List of String): The genres associated with the book.
        rating (Float): The rating of the book.
        publishyear (Int): The year the book was published.
        avaliablecopies (Int): The number of available copies of the book.
        noofreviews (Int): The total number of reviews for the book.
        bookpages (Int): The total number of pages in the book.
    """
    class Meta:
        model = Book
        fields = ("bookid", "title", "isbn", "description", "author", "genres", "rating", "publishyear", "avaliablecopies", "noofreviews", "bookpages")

class BookNode(DjangoObjectType):
    """
    GraphQL Node for querying a Book with additional filtering options.

    Attributes:
        isbn (String): Filter books by exact ISBN.
        title (String): Filter books by exact, case-insensitive, or case-sensitive title match.
        description (String): Filter books by exact, case-insensitive, or case-sensitive description match.
    """
    class Meta:
        model = Book
        filter_fields = {
            "isbn": ['exact'],
            "title": ['exact', "icontains", "istartswith"],
            "description": ['exact', "icontains", 'istartswith'],
        }
        interfaces = (graphene.relay.Node,)

class TransactionsType(DjangoObjectType):
    """
    Represents a GraphQL type for transactions in the library.

    Attributes:
        transactionid (int): The unique identifier for the transaction.
        bookid (int): The identifier of the book associated with the transaction.
        patronid (int): The identifier of the patron involved in the transaction.
        checkoutdate (str): The date when the book was checked out.
        returndate (str): The expected return date for the book.
        finepaid (float): The amount of fine paid for the transaction.
        status (str): The status of the transaction (e.g., checked_out, returned).
    """
    class Meta:
        model = Transactions
        fields = ("transactionid", "bookid", "patronid", "checkoutdate", "returndate", "finepaid", "status")

class BookStatusType(DjangoObjectType):
    """
    Represents a GraphQL type for the status of a book in the library.

    Attributes:
        bookstatusid (int): The unique identifier for the book status.
        bookid (int): The identifier of the associated book.
        customuser (int): The identifier of the custom user (patron) associated with the book status.
        totalpages (int): The total number of pages in the book.
        presentpage (int): The current page the patron has reached in the book.
        status (str): The status of the book (e.g., available, checked_out).
    """
    class Meta:
        model = BookStatus
        fields = ("bookstatusid", "bookid", "customuser", "totalpages", "presentpage", "status")

class ReviewsType(DjangoObjectType):
    """
    Represents a GraphQL type for book reviews in the library.

    Attributes:
        reviewid (int): The unique identifier for the review.
        bookid (int): The identifier of the book associated with the review.
        patronid (int): The identifier of the patron who wrote the review.
        rating (int): The rating given to the book in the review.
        comment (str): The textual comment provided in the review.
    """
    class Meta:
        model = Reviews
        fields = ("reviewid", "bookid", "patronid", "rating", "comment")

class AddToBook(graphene.Mutation):
    """
    This mutation is a super class to inherit from. It aims an promoting DRY by taking care of the frequently written code
    """
    def mutate(self, info):
        """
        Mutate method for AddToBook mutation.

        Args:
            info (graphql.execution.base.ResolveInfo): The GraphQL ResolveInfo object.

        Raises:
            GraphQLError: If the user is not an author or not the author of the book.

        Returns:
            None
        """
        try:
            user = verify_header(info.context)
            if not(user.is_author):
                raise GraphQLError("User is not an author")
            self.book = Book.objects.get(bookid=bookid)
            if not(self.book in user.authoruser.book_set.all()):
                raise GraphQLError("User not an author of Book")
        except Exception as e:
            raise GraphQLError(str(e))

class CreateBookMutation(graphene.Mutation):
    """
    This mutation creates a new book in the library.

    Arguments:
        title (String, required): The title of the book.
        isbn (String, required): The ISBN of the book.
        description (String, required): A brief description of the book.
        genre (String, required): The genre of the book (comma-separated if multiple genres).
        rating (Int): The rating of the book.
        publishyear (Date, required): The publish year of the book.
        avaliablecopies (Int, required): The number of available copies.
        bookpages (Int, required): The number of pages in the book.
    """

    class Arguments:
        title = graphene.String(required=True)
        isbn = graphene.String(required=True)
        description = graphene.String(required=True)
        genre = graphene.String(required=True)
        rating = graphene.Int()
        publishyear = graphene.Date(required=True)
        avaliablecopies = graphene.Int(required=True)
        bookpages = graphene.Int(required=True)

    books = graphene.Field(BookType)

    def mutate(self, info, title, isbn, description, genre, rating, publishyear, avaliablecopies, bookpages):
        """
        Mutate method for CreateBookMutation.

        Args:
            info (graphql.execution.base.ResolveInfo): The GraphQL ResolveInfo object.
            title (str): The title of the book.
            isbn (str): The ISBN of the book.
            description (str): A brief description of the book.
            genre (str): The genre of the book (comma-separated if multiple genres).
            rating (int): The rating of the book.
            publishyear (date): The publish year of the book.
            avaliablecopies (int): The number of available copies.
            bookpages (int): The number of pages in the book.

        Raises:
            GraphQLError: If the user is not an author.

        Returns:
            CreateBookMutation: An instance of CreateBookMutation.
        """
        from genre.models import Genre
        try:
            user = verify_header(info.context)
            author = AuthorUser.objects.get(user=user)

            if not(user.is_author):
                raise GraphQLError("User is not an author")
            new_book = Book()
            new_book.publishyear, new_book.rating = rating, publishyear
            new_book.avaliablecopies, new_book.bookpages = avaliablecopies, bookpages
            new_book.title, new_book.isbn, new_book.description = title, isbn, description
            if "," in genre:
                new_gen = [Genre.objects.get(name=i.strip()) for i in genre.split(',') if get_object_or_404(Genre, name=i.strip())]
                new_book.genres.set(new_gen)
            else:
                if genre.strip() != "":
                    new_book.genres.add(Genre.objects.get(name=genre.strip()))
            new_book.author.set([author])
            new_book.save(using="default")
            return CreateBookMutation()
        except Exception as e:
            raise GraphQLError(str(e))
        
class EditBookMutation(graphene.Mutation):
    """
    This mutation edits the details of an existing book.

    Arguments:
        bookid (String, required): The ID of the book to be edited.
        title (String): The new title of the book.
        isbn (String): The new ISBN of the book.
        description (String): The new description of the book.
        genre (String): The new genre of the book.
        rating (String): The new rating of the book.
        publishyear (String): The new publish year of the book.
        avaliablecopies (String): The new number of available copies.
        bookpages (String): The new number of pages in the book.
    """
    class Arguments:
        bookid = graphene.String(required=True)
        publishyear, avaliablecopies = graphene.String(), graphene.String()
        title, isbn, description = graphene.String(), graphene.String(), graphene.String()
        noofreviews, bookpages, rating = graphene.String(), graphene.String(), graphene.String()
    
    book = graphene.Field(BookType)

    def mutate(self, info, bookid, noofreviews, bookpages, rating,
               publishyear, avaliablecopies, title, isbn, description):
        """
        Mutate method for EditBookMutation.

        Args:
            info (graphql.execution.base.ResolveInfo): The GraphQL ResolveInfo object.
            bookid (str): The ID of the book to be edited.
            noofreviews (str): The new number of reviews for the book.
            bookpages (str): The new number of pages in the book.
            rating (str): The new rating of the book.
            publishyear (str): The new publish year of the book.
            avaliablecopies (str): The new number of available copies.
            title (str): The new title of the book.
            isbn (str): The new ISBN of the book.
            description (str): The new description of the book.

        Raises:
            GraphQLError: If the user is not an author or not the author of the book.

        Returns:
            EditBookMutation: An instance of EditBookMutation.
        """
        try:
            user = verify_header(info.context)
            if not(user.is_author):
                raise GraphQLError("User is not an author")
            book = get_object_or_404(Book, bookid=bookid)
            if not(book in user.authoruser.book.all()):
                raise GraphQLError("User not the author of Book")
            all_query = {
                "title":title, "isbn":isbn, "description": description,
                "noofreviews": noofreviews, "avaliablecopies": avaliablecopies,
                "rating": rating, "publishyear": publishyear, "bookpages": bookpages,
            }
            book.edit_book(**all_query)
            book.save()
            return EditBookMutation()
        except Exception as e:
            raise GraphQLError(str(e))
        
class DeleteBookMutation(graphene.Mutation):
    """
    This mutation deletes an existing book.

    Arguments:
        bookid (String, required): The ID of the book to be deleted.
    """

    class Arguments:
        bookid = graphene.String(required=True)
    
    book = graphene.Field(BookType)

    def mutate(self, info, bookid):
        """
        Mutate method for DeleteBookMutation.

        Args:
            info (graphql.execution.base.ResolveInfo): The GraphQL ResolveInfo object.
            bookid (str): The ID of the book to be deleted.

        Raises:
            GraphQLError: If the user is not an author or not the author of the book.

        Returns:
            DeleteBookMutation: An instance of DeleteBookMutation.
        """
        try:
            user = verify_header(info.context)
            book = get_object_or_404(Book, bookid=bookid)
            if not(user.is_author):
                raise GraphQLError("User is not an author")
            if (book in user.authoruser.book_set.all()):
                raise GraphQLError("User not the author of Book")
            book.delete()
            return DeleteBookMutation()
        except Exception as e:
            raise GraphQLError(str(e))

class AddAuthorToBookMutation(AddToBook, graphene.Mutation):
    """
    Mutation for adding an author to a book.

    Arguments:
        - bookid (str): ID of the book to which the author is added.
        - authorid (str): ID of the author being added.

    Returns:
        - book (BookType): The updated book with the new author.

    Raises:
        - GraphQLError: If any error occurs during the mutation.

    """

    class Arguments:
        bookid = graphene.String(required=True)
        authorid = graphene.String(required=True)

    book = graphene.Field(BookType)

    def mutate(self, info, bookid, authorid):
        """
        Execute the mutation to add an author to a book.

        Parameters:
            - info: GraphQL resolver context.
            - bookid (str): ID of the book to which the author is added.
            - authorid (str): ID of the author being added.

        Returns:
            - AddAuthorToBookMutation: The mutation object.

        Raises:
            - GraphQLError: If any error occurs during the mutation.

        """
        try:
            super().mutate(info)
            author = AuthorUser.objects.get(authorid=authorid)
            if not (author in self.book.author.all()):
                self.book.author.add(author)
                self.book.save()
            return AddAuthorToBookMutation()
        except Exception as e:
            return GraphQLError(str(e))


class AddGenreToBookMutation(AddToBook, graphene.Mutation):
    """
    Mutation for adding a genre to a book.

    Arguments:
        - bookid (str): ID of the book to which the genre is added.
        - genreid (str): ID of the genre being added.

    Returns:
        - book (BookType): The updated book with the new genre.

    Raises:
        - GraphQLError: If any error occurs during the mutation.

    """

    class Arguments:
        bookid = graphene.String(required=True)
        genreid = graphene.String(required=True)

    book = graphene.Field(BookType)

    def mutate(self, info, bookid, genreid):
        """
        Execute the mutation to add a genre to a book.

        Parameters:
            - info: GraphQL resolver context.
            - bookid (str): ID of the book to which the genre is added.
            - genreid (str): ID of the genre being added.

        Returns:
            - AddGenreToBookMutation: The mutation object.

        Raises:
            - GraphQLError: If any error occurs during the mutation.

        """
        try:
            super().mutate(info)
            genre = get_object_or_404(Genre, genreid=genreid)
            if not (genre in self.book.genres.all()):
                self.book.genres.add(genre)
                self.book.save()
            return AddGenreToBookMutation()
        except Exception as e:
            return GraphQLError(str(e))


class RemoveAuthorFromBookMutation(AddToBook, graphene.Mutation):
    """
    Mutation for removing an author from a book.

    Arguments:
        - bookid (str): ID of the book from which the author is removed.
        - authorid (str): ID of the author being removed.

    Returns:
        - book (BookType): The updated book after removing the author.

    Raises:
        - GraphQLError: If any error occurs during the mutation.

    """

    class Arguments:
        bookid = graphene.String(required=True)
        authorid = graphene.String(required=True)

    book = graphene.Field(BookType)

    def mutate(self, info, bookid, authorid):
        """
        Execute the mutation to remove an author from a book.

        Parameters:
            - info: GraphQL resolver context.
            - bookid (str): ID of the book from which the author is removed.
            - authorid (str): ID of the author being removed.

        Returns:
            - RemoveAuthorFromBookMutation: The mutation object.

        Raises:
            - GraphQLError: If any error occurs during the mutation.

        """
        try:
            super().mutate(info)
            author = AuthorUser.objects.get(authorid=authorid)
            if author in self.book.author.all():
                self.book.author.remove(author)
                self.book.save()
            return RemoveAuthorFromBookMutation()
        except Exception as e:
            return GraphQLError(str(e))


class RemoveGenreFromBookMutation(AddToBook, graphene.Mutation):
    """
    Mutation for removing a genre from a book.

    Arguments:
        - bookid (str): ID of the book from which the genre is removed.
        - genreid (str): ID of the genre being removed.

    Returns:
        - book (BookType): The updated book after removing the genre.

    Raises:
        - GraphQLError: If any error occurs during the mutation.

    """

    class Arguments:
        bookid = graphene.String(required=True)
        genreid = graphene.String(required=True)

    book = graphene.Field(BookType)

    def mutate(self, info, bookid, genreid):
        """
        Execute the mutation to remove a genre from a book.

        Parameters:
            - info: GraphQL resolver context.
            - bookid (str): ID of the book from which the genre is removed.
            - genreid (str): ID of the genre being removed.

        Returns:
            - RemoveGenreFromBookMutation: The mutation object.

        Raises:
            - GraphQLError: If any error occurs during the mutation.

        """
        try:
            super().mutate(info)
            genre = get_object_or_404(Genre, genreid=genreid)
            if genre in self.book.genres.all():
                self.book.genres.remove(genre)
                self.book.save()
            return RemoveGenreFromBookMutation()
        except Exception as e:
            return GraphQLError(str(e))


class AddBookToLibraryMutation(graphene.Mutation):
    """
    Mutation to add a book to the user's library.

    Arguments:
        bookid (str): The ID of the book to be added.

    Returns:
        book (BookNode): The added book.
    """

    class Arguments:
        bookid = graphene.String(required=True)

    book = DjangoFilterConnectionField(BookNode)

    def mutate(self, info, bookid):
        """
        Mutate method to add a book to the user's library.

        Parameters:
            info (graphql.execution.base.ResolveInfo): Information about the execution.
            bookid (str): The ID of the book to be added.

        Returns:
            AddBookToLibraryMutation: The mutation result.
        """
        try:
            user = verify_header(info.context)
            book = get_object_or_404(Book, bookid=bookid)
            bookstat = BookStatus(
                bookid=book, totalpages=book.bookpages,
                presentpage=0, status="U", customuser=user 
            )
            bookstat.save()
            return AddBookToLibraryMutation()
        except Exception as e:
            return GraphQLError(str(e))


class RemoveBookFromLibraryMutation(graphene.Mutation):
    """
    Mutation to remove a book from the user's library.

    Arguments:
        bookid (str): The ID of the book to be removed.

    Returns:
        RemoveBookFromLibraryMutation: The mutation result.
    """
     
    class Arguments:
        bookid = graphene.String(required=True)

    def mutate(self, info, bookid):
        """
        Mutate method to remove a book from the user's library.

        Parameters:
            info (graphql.execution.base.ResolveInfo): Information about the execution.
            bookid (str): The ID of the book to be removed.

        Returns:
            RemoveBookFromLibraryMutation: The mutation result.
        """
        try:
            user = verify_header(info.context)
            book = get_object_or_404(Book, bookid=bookid)
            bookstat = BookStatus.objects.filter(
                bookid=book, customuser=user
            )
            bookstat.delete()
            return RemoveBookFromLibraryMutation()
        except Exception as e:
            return GraphQLError(str(e))


class AllBookQuery(graphene.ObjectType):
    """
    Query to retrieve information about books.

    Queries:
        all_book (List[BookNode]): Get all books.
        author_book (List[BookType]): Get books authored by the current user.
        display_library (BookType): Get books in the user's library.
        all_book_node (List[BookNode]): Get all books as nodes.
        single_book (BookType): Get information about a single book.
        read_book (BookStatusType): Get the reading status of a book.
        close_book (BookStatusType): Close the reading status of a book.
    """

    all_book = graphene.List(BookNode)
    author_book = graphene.List(BookType)
    display_library = graphene.Field(BookType)
    all_book_node = DjangoFilterConnectionField(BookNode)
    single_book = graphene.Field(BookType, bookid=graphene.String(required=True))
    read_book = graphene.Field(BookStatusType, bookid=graphene.String(required=True))
    close_book = graphene.Field(
        BookStatusType,
        bookid=graphene.String(required=True),
        pageno=graphene.String(required=True)
    )

    def resolve_all_book(self, info):
        """
        Resolve method to get all books.

        Parameters:
            info (graphql.execution.base.ResolveInfo): Information about the execution.

        Returns:
            QuerySet[Book]: Queryset containing all books.
        """
        return Book.objects.all()
    
    def resolve_author_book(self, info):
        """
        Resolve method to get books authored by the current user.

        Parameters:
            info (graphql.execution.base.ResolveInfo): Information about the execution.

        Returns:
            QuerySet[Book]: Queryset containing books authored by the user.
        """
        user = verify_header(info.context)
        if not(user.is_author):
            raise GraphQLError('User is not an author')
        return user.authoruser.book_set.all()
    
    def resolve_single_book(self, info, bookid):
        """
        Resolve method to get information about a single book.

        Parameters:
            info (graphql.execution.base.ResolveInfo): Information about the execution.
            bookid (str): The ID of the book.

        Returns:
            Book: Book information.
        """
        return Book.objects.get(bookid=bookid)
    
    def resolve_display_library(self, info):
        """
        Resolve method to get books in the user's library.

        Parameters:
            info (graphql.execution.base.ResolveInfo): Information about the execution.

        Returns:
            List[Book]: List of books in the user's library.
        """
        try:
            user = verify_header(info.context)
            bookstat = BookStatus.objects.filter(customuser=user)
            if len(bookstat) > 0:
                return [Book.objects.get(bookid=i.bookid) for i in bookstat]
            return []
        except Exception as e:
            return GraphQLError(str(e))
    
    def resolve_read_book(self, info, bookid):
        """
        Resolve method to get the reading status of a book.

        Parameters:
            info (graphql.execution.base.ResolveInfo): Information about the execution.
            bookid (str): The ID of the book.

        Returns:
            JSONString: JSON string with the read status.
        """
        try:
            user = verify_header(info.context)
            book = Book.objects.get(bookid=bookid)
            bookstat = BookStatus.objects.filter(customuser=user).get(bookid=book)
            bookstat.status = "I"
            bookstat.save()
            return graphene.JSONString({
                "Read": "Successfully Started Reading"
            })
        except Exception as e:
            return GraphQLError(str(e))
        
    def resolve_close_book(self, info, bookid, pageno):
        """
        Resolve method to close the reading status of a book.

        Parameters:
            info (graphql.execution.base.ResolveInfo): Information about the execution.
            bookid (str): The ID of the book.
            pageno (str): The page number.

        Returns:
            BookStatus: The updated book status.
        """
        try:
            user = verify_header(info.context)
            book = Book.objects.get(bookid=bookid)
            bookstat = BookStatus.objects.filter(customuser=user).get(bookid=book)
            bookstat.presentpage = pageno
            bookstat.status = "R" if bookstat.presentpage == bookstat.totalpages else "I"
            bookstat.save()
            return bookstat
        except Exception as e:
            return GraphQLError(str(e))


class BookMutation(graphene.ObjectType):
    """
    Mutation to perform actions related to books.

    Mutations:
        editbook: EditBookMutation for editing a book.
        createbook: CreateBookMutation for creating a new book.
        deletebook: DeleteBookMutation for deleting a book.
        addgenretobook: AddGenreToBookMutation for adding a genre to a book.
        addauthortobook: AddAuthorToBookMutation for adding an author to a book.
        removegenretobook: RemoveGenreFromBookMutation for removing a genre from a book.
        removeauthortobook: RemoveAuthorFromBookMutation for removing an author from a book.
    """
    editbook = EditBookMutation.Field()
    createbook = CreateBookMutation.Field()
    deletebook = DeleteBookMutation.Field()
    addgenretobook = AddGenreToBookMutation.Field()
    addauthortobook = AddAuthorToBookMutation.Field()
    removegenretobook = RemoveGenreFromBookMutation.Field()
    removeauthortobook = RemoveAuthorFromBookMutation.Field()


class BookQuery(AllBookQuery, graphene.ObjectType):
    """
    Combined query for all book-related queries.
    """
    pass
