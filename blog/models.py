from collections import defaultdict

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.
class ActivityLevel(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"

class Goal(models.TextChoices):
    LOSE = "lose", "Lose weight"
    MAINTAIN = "maintain", "Maintain"
    GAIN = "gain", "Gain weight"

class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"

class UserProfile(models.Model):# Макар - дороблю
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="user",
    )
    gender = models.CharField(max_length=10, choices=Gender, verbose_name="Gender")
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(10), MaxValueValidator(100)], verbose_name="Age")
    height_cm = models.PositiveSmallIntegerField(validators=[MinValueValidator(100), MaxValueValidator(250)], verbose_name="Height (cm)",)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(30), MaxValueValidator(300)], verbose_name="Weight (kg)",)
    activity_level = models.CharField(max_length=10,
                                      choices=ActivityLevel.choices, default=ActivityLevel.MEDIUM,
                                      verbose_name="Activity level",)
    goal = models.CharField(max_length=10, choices=Goal.choices, default=Goal.MAINTAIN, verbose_name="Goal")
    calculated_daily_norm = models.PositiveIntegerField(null=True, blank=True, verbose_name="Daily allowence")

    class Meta:
        verbose_name = "User profile"
        verbose_name_plural = "Users profiles"
    def __str__(self):
        return f"Профіль {self.user.username}"

    ACTIVITY_MULTIPLIERS = {
        ActivityLevel.LOW: 1.2,
        ActivityLevel.MEDIUM: 1.55,
        ActivityLevel.HIGH: 1.725,
    }
    GOAL_ADJUSTMENT = {
        Goal.LOSE: -300,
        Goal.MAINTAIN: 0,
        Goal.GAIN: 300,
    }
    SAFE_MINIMUM_CALORIES = 1200

    def calculate_bmr(self) -> float:
        weight = float(self.weight_kg)
        if self.gender == Gender.MALE:
            return 10 * weight + 6.25 * self.height_cm - 5 * self.age + 5
        return 10 * weight + 6.25 * self.height_cm - 5 * self.age - 161

    def calculate_daily_norm(self) -> dict:
        bmr = self.calculate_bmr()
        tdee = bmr * self.ACTIVITY_MULTIPLIERS[self.activity_level]
        adjusted = tdee + self.GOAL_ADJUSTMENT[self.goal]

        result = {
            "calories": None,
            "is_safe": True,
            "warning": (
                "This is a rough estimate for informational purposes only,"
                "not medical advice. For personalized recommendations,"
                "consult a doctor or dietitian."
            ),
        }

        if adjusted < self.SAFE_MINIMUM_CALORIES:
            result["is_safe"] = False
            result["warning"] += (
                f" The calculated rate is below the safe minimum "
                f"({self.SAFE_MINIMUM_CALORIES} kcal/day). Please "
                f"consult a specialist before reducing "
                f"the calorie content of your diet."
            )
        else:
            result["calories"] = round(adjusted)

        return result

class DiaryEntry(models.Model): # Макар - дороблю
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="diary_entries",
        verbose_name="Користувач",
    )
    date = models.DateField(verbose_name="Date")
    product = models.ForeignKey(
        "blog.Product", on_delete=models.CASCADE, null=True, blank=True,
        related_name="diary_entries",
    )
    dish = models.ForeignKey(
        "blog.Dish", on_delete=models.CASCADE, null=True, blank=True,
        related_name="diary_entries",
    )
    amount_grams = models.PositiveIntegerField(
        verbose_name="Amount (g)",
        help_text="Weight of food consumed in grams (for a dish—the weight of a serving)",
    )
    calories = models.PositiveIntegerField(
        verbose_name="Calories Calculated",
        help_text="Filled in automatically upon saving",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log entry"
        verbose_name_plural = "Log entries"
        ordering = ["-date", "-created_at"]
        indexes = [models.Index(fields=["user", "date"])]
        constraints = [
            models.CheckConstraint(
                condition=(
                        models.Q(product__isnull=False, dish__isnull=True)
                        | models.Q(product__isnull=True, dish__isnull=False)
                ),
                name="diary_entry_exactly_one_of_product_or_dish",
            )
        ]

    def __str__(self):
        item = self.product or self.dish
        return f"{self.user.username} — {item} ({self.date})"

    def save(self, *args, **kwargs):
        if self.product:
            self.calories = round(self.product.calories_per_100g * self.amount_grams / 100)
        elif self.dish:
            self.calories = round(self.dish.calories * self.amount_grams / 100)
        super().save(*args, **kwargs)

## Volodymyr

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="Product Name")
    calories_per_100g = models.PositiveIntegerField(verbose_name="Calories per 100g")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Category")
    protein_per_100g = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Protein per 100g")
    fat_per_100g = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fat per 100g")
    carbs_per_100g = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Carbohydrates per 100g")

    def __str__(self):
        return self.name

class Dish(models.Model):
    name = models.CharField(max_length=100, verbose_name="Dish Name")
    description = models.TextField(blank=True, verbose_name="Description")
    calories = models.PositiveIntegerField(null=True, blank=True, verbose_name="Calories")
    
    ingridients = models.ManyToManyField(
        Product,
        through="DishIngredient",
        related_name="dishes",
        verbose_name="Ingridients"
    )
    
    def get_calories(self):
        if self.ingridients.exists():
            total = sum(ingridient.weight_grams / 100 * ingridient.product.calories_per_100g 
                        for ingridient in self.dishingredients.select_related('product'))
            return round(total)
        return self.calories
    
    def __str__(self):
        return self.name
    
class DishIngredient(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name="dishingredients")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    weight_grams = models.PositiveIntegerField(verbose_name="Weight in grams")
    
    def __str__(self):
        return f"{self.weight_grams}g of {self.product.name} in {self.dish.name}"
    
    class Meta:
        unique_together = ("dish", "product")