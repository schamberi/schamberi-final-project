# Generated by Django 5.0 on 2023-12-12 16:09

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cashflow",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cashflow_id", models.CharField(max_length=20)),
                ("loan_id", models.CharField(max_length=20)),
                ("cashflow_date", models.DateField(null=True)),
                ("cashflow_currency", models.CharField(max_length=3)),
                (
                    "cashflow_type",
                    models.CharField(
                        choices=[("funding", "Funding"), ("repayment", "Repayment")],
                        max_length=9,
                    ),
                ),
                (
                    "cashflow_amount",
                    models.DecimalField(decimal_places=2, max_digits=12),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Trades",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("loan_id", models.CharField(max_length=20)),
                ("investment_date", models.DateField(null=True)),
                ("maturity_date", models.DateField(null=True)),
                ("interest_rate", models.DecimalField(decimal_places=2, max_digits=4)),
            ],
        ),
    ]
