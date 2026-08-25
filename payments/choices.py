from django.db import models


class PaymentMethod(models.TextChoices):
    COD = 'cod', 'Cash on Delivery'
    UPI = 'upi', 'UPI'
    CARD = 'card', 'Credit / Debit Card'
    NETBANKING = 'netbanking', 'Net Banking'
    WALLET = 'wallet', 'Wallet'


COD_THRESHOLD = 300