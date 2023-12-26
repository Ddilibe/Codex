from account.models import CustomUser, AuthorUser, PatronUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from collections.abc import Collection, Iterable
from django.urls import reverse
from genre.models import Genre
from django.db import models
from uuid import uuid4
import math

# Create your models here.
class Book(models.Model):
    """Class: Book

    Represents a book in the library.

    Attributes:
    - bookid (UUIDField): A unique identifier for the book.
    - title (CharField): The title of the book.
    - isbn (CharField): The ISBN of the book.
    - description (TextField): A description of the book.
    - author (ManyToManyField): Many-to-many relationship with AuthorUser.
    - genres (ManyToManyField): Many-to-many relationship with Genre.
    - created_at (DateTimeField): Date and time when the book was created.
    - updated_at (DateTimeField): Date and time when the book was last updated.
    - rating (IntegerField): The rating of the book.
    - publishyear (DateField): The year of publication.
    - available_copies (IntegerField): The number of available copies.
    - no_of_reviews (IntegerField): The number of reviews for the book.
    - book_pages (IntegerField): The number of pages in the book.

    Methods:
    - __str__: Returns a string representation of the book.
    - get_absolute_url: Returns the absolute URL for the book.
    - calculate_book_rating: Calculates and updates the book's rating based on reviews.
    - edit_book: Edits the book's attributes based on the provided keyword arguments.

    """
    bookid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=256)
    isbn = models.CharField(max_length=50)
    description = models.TextField(_("Description"))
    author = models.ManyToManyField(AuthorUser, verbose_name=_("Author"))
    genres = models.ManyToManyField(Genre, verbose_name=_("Genre"))
    created_at = models.DateTimeField(_("Created At"), auto_now=True, auto_now_add=False)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=False, auto_now_add=True)
    rating = models.IntegerField(_("Rating"), default=0)
    publishyear = models.DateField(_("Year Of Publish"))
    avaliablecopies = models.IntegerField(_("Avaliable Copies"))
    noofreviews = models.IntegerField(_("No of Reviews"))
    bookpages = models.IntegerField(_("Number Of Book Pages"))

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def __str__(self):
        string = f" Title: {self.title}\n ISBN: {self.isbn}\n Author: {[i.user.username for i in self.Author.all()]}\n"
        string += f" Genre: {[i.name for i in self.genres.all()]}\n Avaliable Copies: {self.avaliablecopies}"
        return string

    def get_absolute_url(self):
        return reverse("Transactions_detail", kwargs={"pk": self.pk})
    
    def calculate_book_rating(self):
        books = Reviews.objects.filter(bookid=self.bookid)
        self.rating = sum([i.rating for i in books])/len(books)
        self.noofreviews = len([i.rating for i in books if i.rating > 0])
        return
    
    def edit_book(self, **kwargs):
        self.isbn = kwargs.get('isbn') if "isbn" in kwargs.keys() else self.isbn
        self.title = kwargs.get('title`') if "title" in kwargs.keys() else self.title
        self.rating = kwargs.get("rating") if "rating" in kwargs.keys() else self.rating
        self.bookpages = kwargs.get("bookpages") if "bookpages" in kwargs.keys() else self.bookpages
        self.description = kwargs.get("description") if "description" in kwargs.keys() else self.description
        self.publishyear = kwargs.get("publishyear") if "publishyear" in kwargs.keys() else self.publishyear
        self.noofreviews = kwargs.get("noofreviews") if "noofreviews" in kwargs.keys() else self.noofreviews
        self.avaliablecopies = kwargs.get("avaliablecopies") if "avaliablecopies" in kwargs.keys() else self.avaliablecopies

    


class Transactions(models.Model):
    """Class: Transactions

    Represents transactions involving the checkout and return of books by patrons.

    Attributes:
    - transactionid (UUIDField): A unique identifier for the transaction.
    - bookid (ForeignKey): Foreign key relationship with Book.
    - patronid (ForeignKey): Foreign key relationship with PatronUser.
    - checkoutdate (DateField): Date when the book was checked out.
    - returndate (DateField): Date when the book is due to be returned.
    - fineamount (IntegerField): Amount of fine for overdue books.
    - finepaid (BooleanField): Indicates whether the fine has been paid.
    - status (CharField): Status of the transaction ('Checked Out', 'Returned', 'Lost').
    - created_at (DateTimeField): Date and time when the transaction was created.
    - updated_at (DateTimeField): Date and time when the transaction was last updated.

    Methods:
    - __str__: Returns a string representation of the transaction.
    - get_absolute_url: Returns the absolute URL for the transaction.
    - change_fine_amount: Changes the default fine amount for overdue books.

    """
    transactionid = models.UUIDField(_("Transaction ID"), primary_key=True, default=uuid4)
    bookid = models.ForeignKey(Book, verbose_name=_("Book ID"), on_delete=models.CASCADE)
    patronid = models.ForeignKey(PatronUser, verbose_name=_("Patron ID"), on_delete=models.CASCADE)
    checkoutdate = models.DateField(_("Checkout Date"), auto_now=False, auto_now_add=False)
    returndate = models.DateField(_("Return Date"), auto_now=False, auto_now_add=False)
    fineamount = 400 # This amount can be changed
    finepaid = models.BooleanField(_("Fine Paid"), default=False)
    status = models.CharField(max_length=20, choices=[('C', 'Checked Out'), ('R', 'Returned'), ('L', 'Lost')])
    created_at = models.DateTimeField(_("Created At"), auto_now=True, auto_now_add=False)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = _("Transactions")
        verbose_name_plural = _("Transactionss")

    def __str__(self):
        return f"Transaction {self.transactionid}\n Book: {self.bookid.title}\n Patron: {self.patronid.user.username}\n Status: {self.status}"

    def get_absolute_url(self):
        return reverse("Transactions_detail", kwargs={"pk": self.pk})
    
    @classmethod
    def change_fine_amount(cls, value):
        cls.fineamount = value

class BookStatus(models.Model):
    """Class: BookStatus

    Represents the reading status of a book for a specific patron.

    Attributes:
    - bookstatusid (UUIDField): A unique identifier for the book status.
    - bookid (ForeignKey): Foreign key relationship with Book.
    - customuser (ForeignKey): Foreign key relationship with CustomUser.
    - totalpages (IntegerField): Total number of pages in the book.
    - presentpage (IntegerField): Current page the patron has reached.
    - status (CharField): Status of reading progress ('read', 'Incomplete', 'unread').

    Methods:
    - __str__: Returns a string representation of the book status.
    - save: Overrides the save method to set totalpages based on the associated book.

    """

    bookstatusid = models.UUIDField(_("Book Status ID"), default=uuid4, primary_key=True)
    bookid = models.ForeignKey(Book, verbose_name=_("Book ID"), on_delete=models.CASCADE)
    customuser = models.ForeignKey(CustomUser, verbose_name=_("Patron ID"), on_delete=models.CASCADE)
    totalpages = models.IntegerField(_("Total Number Of Pages"))
    presentpage = models.IntegerField(_("Present Page"), default=0)
    status = models.CharField(_("Status"), max_length=50, choices=[('R', 'read'), ('I', "Incomplete"), ('U', "unread")])

    class Meta:
        verbose_name = _("BookStatus")
        verbose_name_plural = _("BookStatuss")

    def __str__(self):
        return f"Book Name: {self.bookid.title}\n User: {self.customuser.username}\n Present Page: {self.presentpage}\n Total Page: {self.totalpages}"
    
    def save(self):
        from books.models import Book
        self.totalpages = Book.objects.get(bookid=self.bookid).bookpages
        return super().save()

    def get_absolute_url(self):
        return reverse("Genre_detail", kwargs={"pk": self.pk})

class Reviews(models.Model):
    """Class: Reviews

    Represents reviews given by patrons for books.

    Attributes:
    - reviewid (UUIDField): A unique identifier for the review.
    - bookid (ForeignKey): Foreign key relationship with Book.
    - patronid (ForeignKey): Foreign key relationship with PatronUser.
    - rating (IntegerField): Rating given by the patron.
    - comment (TextField): Comment provided by the patron.
    - created_at (DateTimeField): Date and time when the review was created.
    - updated_at (DateTimeField): Date and time when the review was last updated.

    Methods:
    - __str__: Returns a string representation of the review.
    - get_absolute_url: Returns the absolute URL for the review.
    - validate_constraints: Validates constraints on the review (e.g., rating within 0 and 5).
    - save: Overrides the save method to update the associated book's rating.

    """

    reviewid = models.UUIDField(_("Review ID"), default=uuid4, primary_key=True)
    bookid = models.ForeignKey(Book, verbose_name=_("Book ID"), on_delete=models.CASCADE)
    patronid = models.ForeignKey(PatronUser, verbose_name=_("Patron ID"), on_delete=models.CASCADE)
    rating = models.IntegerField(_("Rating"))
    comment = models.TextField(_("Commment"))
    created_at = models.DateTimeField(_("Created At"), auto_now=True, auto_now_add=False)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = _("Reviews")
        verbose_name_plural = _("Reviewss")

    def __str__(self):
        return f"Book Name: {self.bookid.title}\n Patron Name: {self.patronid.user.username}\n Rating: {self.rating}\n Comment: {self.comment}"

    def get_absolute_url(self):
        return reverse("Reviews_detail", kwargs={"pk": self.pk})
    
    def validate_constraints(self, exclude: Collection[str] | None) -> None:
        if self.rating > 5 or self.rating < 0:
            raise ValidationError(f"Rating should be within 0 and 5")
        return super().validate_constraints(exclude)

    def save(self, ) -> None:
        new_rating = math.round(self.rating/5)
        self.bookid.rating = new_rating
        self.bookid.save()
        return super().save()
    