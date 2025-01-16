from django.db import models


class TriangleData(models.Model):
    period_start = models.DateField()
    period_end = models.DateField()
    evaluation_date = models.DateField()
    earned_premium = models.DecimalField(max_digits=15, decimal_places=2)
    reported_loss = models.DecimalField(max_digits=15, decimal_places=2)
    paid_loss = models.DecimalField(max_digits=15, decimal_places=2)
    program = models.CharField(max_length=100)
    dev_lag = models.IntegerField()

    def __str__(self):
        return f"{self.program}: {self.period_start} - {self.period_end}"

    class Meta:
        app_label = "api"
