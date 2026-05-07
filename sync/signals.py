"""
Gamestore → Backup DB Sync Signals
====================================
Listens for save/delete events on every Gamestore model and mirrors
the change to the backup database.

Direction: Gamestore (default) → Backup DB (one-way only)

Sync order respects FK dependencies:
  User → Topic → Category → Product
        → ShippingAddress → Order → OrderItem → RefundRequest → RefundItem
        → RewardAccount → RewardTransaction
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver

from store.models import Topic, Category, Product
from payment.models import ShippingAddress, Order, OrderItem, RefundRequest, RefundItem
from account.models import RewardAccount, RewardTransaction

logger = logging.getLogger(__name__)

SYNC_TARGETS = ['backup', 'separate']

# Tracks which PKs are currently being synced to prevent recursion
_syncing = set()

# ─────────────────────────────────────────────
# Core sync helpers
# ─────────────────────────────────────────────

def mirror_save(instance):
    """
    Save an instance to the backup database.
    Errors are logged but never crash the primary write.
    """
    key = (instance.__class__.__name__, instance.pk)
    if key in _syncing:
        return   # already syncing this instance, stop recursion
    _syncing.add(key)
    try:
        for db in SYNC_TARGETS:
            try:
                instance.save(using=db)
            except Exception as e:
                logger.error("[Sync] Save failed for %s (pk=%s) on %s: %s",
                             instance.__class__.__name__, instance.pk, db, e)
    finally:
        _syncing.discard(key)


def mirror_delete(instance):
    """
    Delete an instance from the backup database by pk.
    Errors are logged but never crash the primary delete.
    """
    for db in SYNC_TARGETS:
        try:
            type(instance).objects.using(db).filter(pk=instance.pk).delete()
        except Exception as e:
            logger.error("[Sync] Delete failed for %s (pk=%s) on %s: %s",
                         instance.__class__.__name__, instance.pk, db, e)


# ─────────────────────────────────────────────
# User (Django built-in)
# Must sync first — all other models FK to User
# ─────────────────────────────────────────────

@receiver(post_save, sender=User)
def sync_user_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=User)
def sync_user_delete(sender, instance, **kwargs):
    mirror_delete(instance)


# ─────────────────────────────────────────────
# store app — Topic, Category, Product
# ─────────────────────────────────────────────

@receiver(post_save, sender=Topic)
def sync_topic_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=Topic)
def sync_topic_delete(sender, instance, **kwargs):
    mirror_delete(instance)


@receiver(post_save, sender=Category)
def sync_category_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=Category)
def sync_category_delete(sender, instance, **kwargs):
    mirror_delete(instance)


@receiver(post_save, sender=Product)
def sync_product_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=Product)
def sync_product_delete(sender, instance, **kwargs):
    mirror_delete(instance)


# ─────────────────────────────────────────────
# payment app — ShippingAddress, Order,
#               OrderItem, RefundRequest, RefundItem
# ─────────────────────────────────────────────

@receiver(post_save, sender=ShippingAddress)
def sync_shipping_address_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=ShippingAddress)
def sync_shipping_address_delete(sender, instance, **kwargs):
    mirror_delete(instance)


@receiver(post_save, sender=Order)
def sync_order_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=Order)
def sync_order_delete(sender, instance, **kwargs):
    mirror_delete(instance)


@receiver(post_save, sender=OrderItem)
def sync_order_item_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=OrderItem)
def sync_order_item_delete(sender, instance, **kwargs):
    mirror_delete(instance)


@receiver(post_save, sender=RefundRequest)
def sync_refund_request_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=RefundRequest)
def sync_refund_request_delete(sender, instance, **kwargs):
    mirror_delete(instance)


@receiver(post_save, sender=RefundItem)
def sync_refund_item_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=RefundItem)
def sync_refund_item_delete(sender, instance, **kwargs):
    mirror_delete(instance)


# ─────────────────────────────────────────────
# account app — RewardAccount, RewardTransaction
# ─────────────────────────────────────────────

@receiver(post_save, sender=RewardAccount)
def sync_reward_account_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=RewardAccount)
def sync_reward_account_delete(sender, instance, **kwargs):
    mirror_delete(instance)


@receiver(post_save, sender=RewardTransaction)
def sync_reward_transaction_save(sender, instance, **kwargs):
    mirror_save(instance)

@receiver(post_delete, sender=RewardTransaction)
def sync_reward_transaction_delete(sender, instance, **kwargs):
    mirror_delete(instance)