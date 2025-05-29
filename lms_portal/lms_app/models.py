from django.db import models


class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    contact_info = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.genre_name


class Member(models.Model):
    member_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    MEMBERSHIP_TYPES = [
        ('Standard', 'Standard'),
        ('Premium', 'Premium'),
    ]

    membership_id = models.AutoField(primary_key=True)
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE)
    membership_type = models.CharField(max_length=10, choices=MEMBERSHIP_TYPES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.member.name} - {self.membership_type}"


class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.username


class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    year_of_publication = models.PositiveSmallIntegerField(null=True, blank=True)
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField()
    author_id = models.ForeignKey(Author, null=True, blank=True, on_delete=models.SET_NULL)
    genre_id = models.ForeignKey(Genre, null=True, blank=True, on_delete=models.SET_NULL)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return self.title


class BookIssue(models.Model):
    issue_id = models.AutoField(primary_key=True)
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL)
    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} -> {self.member.name}"


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE)
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    review_text = models.TextField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Review by {self.member.name} on {self.book.title}"


class Fine(models.Model):
    FINE_STATUS = [
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    ]

    fine_id = models.AutoField(primary_key=True)
    issue_id = models.ForeignKey(BookIssue, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=FINE_STATUS, default='Unpaid')
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Fine {self.fine_id} - {self.status}"


class Transaction(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online', 'Online'),
    ]

    transaction_id = models.AutoField(primary_key=True)
    membership_id = models.ForeignKey(Membership, null=True, blank=True, on_delete=models.CASCADE)
    fine_id = models.ForeignKey(Fine, null=True, blank=True, on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    payment_date = models.DateField()

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.payment_method}"
