from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError

from uuid import uuid4
from azbankgateways.models.banks import Bank

# Create your models here.


class OrderStatusManager:
    def __init__(self, order):
        self.order = order

    def process_payment(self, selected_bank):
        if selected_bank not in dict(BankTypes.choices):
            raise ValueError("Invalid bank type")
        self.order.bank_type = selected_bank
        self.change_status(Status.PAID)

    def cancel(self):
        self.change_status(Status.CANCELLED)

    def process(self):
        self.change_status(Status.PROCESSING)

    def ship(self):
        self.change_status(Status.SHIPPED)

    def deliver(self):
        self.change_status(Status.DELIVERED)

    def change_status(self, new_status):
        if not self._is_valid_transition(new_status):
            raise ValidationError(
                f"Invalid status transition from {self.order.status} to {new_status}")

        old_status = self.order.status
        self.order.status = new_status
        self.order.save()

        OrderStatusLog.objects.create(
            order=self.order,
            old_status=old_status,
            new_status=new_status,
        )

    def _is_valid_transition(self, new_status):
        valid_transitions = {
            Status.PENDING: [Status.PAID, Status.CANCELLED],
            Status.PAID: [Status.PROCESSING, Status.CANCELLED],
            Status.PROCESSING: [Status.SHIPPED, Status.CANCELLED],
            Status.SHIPPED: [Status.DELIVERED, Status.CANCELLED],
            Status.DELIVERED: [],
            Status.CANCELLED: []
        }
        return new_status in valid_transitions.get(self.order.status, [])

    @property
    def is_paid(self) -> bool:
        return self.status == self.Status.PAID


class Status(models.TextChoices):
    PENDING = 'PENDING', _('pending')
    PROCESSING = 'PROCESSING', _('processing')
    PAID = 'PAID', _('paid')
    SHIPPED = 'SHIPPED', _('shipped')
    DELIVERED = 'DELIVERED', _('delivered')
    CANCELLED = 'CANCELLED', _('cancelled')


class BankTypes(models.TextChoices):
    ZARINPAL = 'ZARINPAL', _('zarinpal')
    IDPAY = 'IDPAY', _('idpay')

class Address(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='addresses')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}, {self.postal_code}"

class Order(models.Model):
    user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.CASCADE, related_name='orders')
    addresses = models.ManyToManyField(Address, related_name='orders', blank=True)

    promotion_coupon = models.ForeignKey(
        'carts.Promotion', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders',)

    bank_record = models.OneToOneField(
        Bank, on_delete=models.CASCADE, default=None, null=True, blank=True)
    bank_type = models.CharField(
        max_length=8, choices=BankTypes.choices, null=True)

    order_number = models.CharField(max_length=32, unique=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['status', 'is_active']),
        ]
        permissions = [
            ("can_cancel_order", "Can cancel order"),
            ("can_process_order", "Can process order"),
        ]

    def __str__(self) -> str:
        return f"Order {self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = str(uuid4().hex)[:32]
        super().save(*args, **kwargs)


class OrderStatusLog(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='status_logs')
    created_by = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=16, choices=Status.choices)
    new_status = models.CharField(max_length=16, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order Status Log'
        verbose_name_plural = 'Order Status Logs'

    def __str__(self):
        return f"{self.order.order_number}: {self.old_status} -> {self.new_status}"
