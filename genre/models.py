from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db import models
from uuid import uuid4

class Genre(models.Model):
    """
    Represents a genre in the library.

    Attributes:
        genreid (UUID): A unique identifier for the genre.
        name (str): The name of the genre.
        description (str): The description of the genre.

    Meta:
        verbose_name (str): A human-readable singular name for the model.
        verbose_name_plural (str): A human-readable plural name for the model.

    Methods:
        __str__: Returns a string representation of the genre.
        get_absolute_url: Returns the URL for the genre's detail view.

    Usage:
        genre = Genre.objects.create(name='Mystery', description='A genre of literature or movies that deals with secrets, puzzles, and suspense.')
    """

    genreid = models.UUIDField(_("Genre ID"), default=uuid4, primary_key=True)
    name = models.CharField(_("Genre Name"), max_length=50)
    description = models.TextField(_("Description"))

    class Meta:
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        """
        Returns a string representation of the genre.

        Returns:
            str: A string with the genre name and description.
        """
        return f"\n Genre Name : {self.name}\n Description: {self.description}"

    def get_absolute_url(self):
        """
        Returns the URL for the genre's detail view.

        Returns:
            str: The URL for the genre's detail view.
        """
        return reverse("genre_detail", kwargs={"pk": self.genreid})
