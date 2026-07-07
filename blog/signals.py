from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DishIngredient, Dish


# Making signal reveiver for updating calories
@receiver(post_save, sender=DishIngredient)
@receiver(post_delete, sender=DishIngredient)
def update_dish_calories(sender, instance, **kwargs):
    dish = instance.dish
    dish.calories = dish.get_calories()
    dish.save(update_fields=['calories'])