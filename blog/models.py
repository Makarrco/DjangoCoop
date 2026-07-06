from collections import defaultdict

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from numpy.random.mtrand import choice


# Create your models here.
class ActivityLevel(models.TextChoices):
    LOW = "low", "Низький"
    MEDIUM = "medium", "Середній"
    HIGH = "high", "Високий"


class Goal(models.TextChoices):
    LOSE = "lose", "Схуднути"
    MAINTAIN = "maintain", "Зберегти вагу"
    GAIN = "gain", "Набрати вагу"

class Gender(models.TextChoices):
    MALE = "male", "Чоловіча"
    FEMALE = "female", "Жіноча"

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
                                      verbose_name="Рівень активності",)
    goal = models.CharField(max_length=10, choices=Goal.choices, default=Goal.MAINTAIN, verbose_name="Goal")
    calculated_daily_norm = models.PositiveIntegerField(null=True, blank=True, verbose_name="Розрахована денна норма")

    class Meta:
        verbose_name = "User profile"
        verbose_name_plural = "Профілі користувачів"
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
                "Це орієнтовний розрахунок для інформаційних цілей, "
                "не медична порада. Для індивідуальних рекомендацій "
                "зверніться до лікаря чи дієтолога."
            ),
        }

        if adjusted < self.SAFE_MINIMUM_CALORIES:
            result["is_safe"] = False
            result["warning"] += (
                f" Розрахована норма нижча за безпечний мінімум "
                f"({self.SAFE_MINIMUM_CALORIES} ккал/день). Будь ласка, "
                f"проконсультуйтеся з фахівцем перед тим, як зменшувати "
                f"калорійність раціону."
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
    date = models.DateField(verbose_name="Дата")
    product = models.ForeignKey(
        "blog.Product", on_delete=models.CASCADE, null=True, blank=True,
        related_name="diary_entries",
    )
    dish = models.ForeignKey(
        "blog.Dish", on_delete=models.CASCADE, null=True, blank=True,
        related_name="diary_entries",
    )
    amount_grams = models.PositiveIntegerField(
        verbose_name="Кількість (г)",
        help_text="Вага з'їденого в грамах (для страви — вага порції)",
    )
    calories = models.PositiveIntegerField(
        verbose_name="Розраховані калорії",
        help_text="Заповнюється автоматично при збереженні",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запис щоденника"
        verbose_name_plural = "Записи щоденника"
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

####Volodymur