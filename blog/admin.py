from django.contrib import admin
from .models import Category, Dish, DishIngredient, Product

# Register your models here.

@admin.register(Category) # Прикольний 
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "calories_per_100g", "protein_per_100g", "fat_per_100g", "carbs_per_100g"]
    list_filter = ["category"]
    search_fields = ["name"]

class DishIngredientInline(admin.TabularInline):
    model = DishIngredient
    extra = 3

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ["name", "get_calories"]
    search_fields = ["name"]
    inlines = [DishIngredientInline]
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save()
        dish = formset.instance
        
        if dish.ingredients.exists():
            dish.calories = dish.get_calories()
            dish.save(update_fields=['calories'])
