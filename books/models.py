from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    class CoverType(models.TextChoices):
        HARD = "HARD", "HARD"
        SOFT = "SOFT", "SOFT"

    cover = models.CharField(
        max_length=4,
        choices=CoverType.choices,
    )

    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    def __str__(self):
        return self.title