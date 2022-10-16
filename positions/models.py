from django.db import models
from invoices.models import Invoice


class Position(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="optional info")
    amount = models.FloatField(help_text='the amount is in USD')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'invoice: {self.invoice.number}, position title: {self.title}'
