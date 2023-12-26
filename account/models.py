from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.urls import reverse
from uuid import uuid4


class CustomUserManager(BaseUserManager):
    """
    Manager for the CustomUser model. Provides methods for creating regular users and superusers.
    """

    def create_user(self, email, password=None, **kwargs):
        """
        Create and return a regular user with an email and password.

        Parameters:
            - email (str): The user's email address.
            - password (str): The user's password.
            - **kwargs: Additional user data.

        Returns:
            CustomUser: The created user instance.
        """
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        """
        Create and return a superuser with an email, password, and additional attributes.

        Parameters:
            - email (str): The superuser's email address.
            - password (str): The superuser's password.
            - **kwargs: Additional superuser data.

        Returns:
            CustomUser: The created superuser instance.
        """
        kwargs.setdefault("is_admin", True)
        kwargs.setdefault("is_author", True)
        kwargs.setdefault("is_patron", True)

        return self.create_user(email, password, **kwargs)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that extends AbstractBaseUser and PermissionsMixin.
    Represents users with different roles in the system.
    """

    pos = [
        ('L', "Library User"),
        ("P", "Patron"),
        ("A", "Author"),
        ("D", "Admin"),
    ]
    email = models.EmailField(unique=True)
    username = models.CharField(_("Username"), max_length=50, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_patron = models.BooleanField(default=False)
    is_author = models.BooleanField(default=False)
    token = models.CharField(max_length=255, null=True, blank=True, unique=True)
    role = models.CharField(max_length=1, choices=pos, default='L')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        """
        String representation of the user.

        Returns:
            str: User details as a string.
        """
        return f"Username: {self.username}\n First Name: {self.first_name}\n Last Name: {self.last_name}\n Email Address: {self.email}\n Role: {self.role}"
    

    class Meta:
        permissions = [
            ('read', "Can read a book"),
            ('review', "Can leave reviews")
        ]


class PatronUser(models.Model):
    """
    Model representing a patron user with additional details.
    """

    patronid = models.UUIDField(_("Patron ID"), default=uuid4, primary_key=True)
    user = models.OneToOneField("CustomUser", verbose_name=_("User Profile"), on_delete=models.CASCADE)
    address = models.CharField(_("Address"), max_length=50)
    phone_number = PhoneNumberField(_("Phone Number"))
    created_at = models.DateTimeField(_("Created At"), auto_now=True, auto_now_add=False)
    updated_at = models.DateTimeField(_("Created At"), auto_now=False, auto_now_add=True)


    class Meta:
        verbose_name = _("PatronUser")
        verbose_name_plural = _("PatronUsers")
        permissions = [
            ("borrow", "Can borrow a book"),
            ("return", "Can return a book")
        ]

    def __str__(self):
        """
        String representation of the patron user.

        Returns:
            str: Patron user details as a string.
        """
        return f"Patron Name: {self.user.username}\n Address: {self.address}\n Phone Number: {self.phone_number}"

    def get_absolute_url(self):
        """
        Get the absolute URL for the patron user.

        Returns:
            str: The absolute URL for the patron user.
        """
        return reverse("PatronUser_detail", kwargs={"pk": self.pk})
    

class AuthorUser(models.Model):
    """
    Model representing an author user with additional details.
    """

    author_id = models.UUIDField(_("Author Id"), default=uuid4, primary_key=True)
    user = models.OneToOneField("CustomUser", verbose_name=_("User Profile"), on_delete=models.CASCADE)
    birthdate = models.DateField(_("Birth Date"), auto_now=False, auto_now_add=False)
    nationality = models.CharField(_("Nationality"), max_length=50)
    created_at = models.DateTimeField(_("Created At"), auto_now=True, auto_now_add=False)
    updated_at = models.DateTimeField(_("Created At"), auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = _("AuthorUser")
        verbose_name_plural = _("AuthorUsers")
        permissions = [
            ('write', "Can write a book"),
            ('publish', "Can publish a book"),
            ('edit', "Can edit an unpublished book"),
            ('delete', "Can delete an unpublished book")
        ]

    def __str__(self):
        """
        String representation of the author user.

        Returns:
            str: Author user details as a string.
        """
        return f"Author Name: {self.user.username}\n Birthdate: {self.birthdate}\n Nationality: {self.nationality}"

    def get_absolute_url(self):
        """
        Get the absolute URL for the author user.

        Returns:
            str: The absolute URL for the author user.
        """
        return reverse("AuthorUser_detail", kwargs={"pk": self.pk})
