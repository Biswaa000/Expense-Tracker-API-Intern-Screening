from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)

    monthly_limit = models.DecimalField(
        max_digits=10,      # Maximum 10 digits total
        decimal_places=2,    # 2 digits after decimal point
        null=True,           # Can be NULL in database
        blank=True           # Can be empty in forms
    )

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Expense(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses"
    )
    
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    currency = models.CharField(
            max_length=3,           # ISO currency codes: USD, EUR, GBP, JPY, etc.
            default="USD"           # Default currency if none specified
        )

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="expenses"
    )
    date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.amount} {self.currency})"
