from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import ProfileForm, DiaryEntryForm, SearchForm
from .models import UserProfile, DiaryEntry, Dish, DishIngredient, Product, Category

from django.http import HttpResponse
from django.db import transaction
from django.core.paginator import Paginator


def home_view(request):
    return render(request, "home.html")


###profile
@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return redirect("profile_create")
    norm = profile.calculate_daily_norm()
    return render(request, "accounts/profile.html", {"profile": profile, "norm": norm})
@login_required
def profile_edit_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)  # тільки свій
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile_form.html", {"form": form})


##diary

@login_required
def diary_view(request):
    entries = DiaryEntry.objects.filter(user=request.user).select_related("product", "dish")
    daily_totals = {}
    for entry in entries:
        daily_totals.setdefault(entry.date, 0)
        daily_totals[entry.date] += entry.calories
    norm = None
    if hasattr(request.user, "profile"):
        norm = request.user.profile.calculate_daily_norm()

    return render(request,
        "diary/diary.html",
        {"entries": entries, "daily_totals": daily_totals, "norm": norm},
    )
@login_required
def diary_add_view(request):
    if request.method == "POST":
        form = DiaryEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user  # НІКОЛИ не бери user з форми/POST
            entry.save()
            return redirect("diary")
    else:
        form = DiaryEntryForm()

    return render(request, "diary/diary_add.html", {"form": form})
@login_required
def diary_delete_view(request, pk):
    """Фільтр user=request.user гарантує: не можна видалити чужий запис,
    навіть підставивши чужий pk в URL."""
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        return redirect("diary")
    return render(request, "diary/diary_confirm_delete.html", {"entry": entry})

####### Volodymur

# @login_required
def search_panel(request):
    form = SearchForm(request.POST or None)
    products = Product.objects.none()
    dishes = Dish.objects.none()
    query = ""
    if form.is_valid():
        query = form.cleaned_data["name"]
        category = form.cleaned_data["category"]
        if query:
            products = Product.objects.filter(name__icontains=query)
            dishes = Dish.objects.filter(name__icontains=query)
        else:
            products = Product.objects.all()
            dishes = Dish.objects.all()        
        if category:
            products = products.filter(category__name__icontains=category)
            dishes = dishes.filter(ingridients__category__name__icontains=category)
        
    return render(request, "searchpanel/search.html", {
        "form": form,
        "query": query,
        "products": products,
        "dishes": dishes,
    })

def error(request, rest):
    return render(request, "404.html")


CATEGORIES = [
    "Овочі", "Фрукти", "М'ясо", "Риба", "Молочні продукти",
    "Крупи", "Хлібобулочні", "Горіхи та насіння", "Бобові", "Напої",
]
PRODUCTS = [
    ("Куряча грудка", 165, 31.0, 3.6, 0.0, "М'ясо"),
    ("Яловичина", 250, 26.0, 15.0, 0.0, "М'ясо"),
    ("Свинина", 242, 27.0, 14.0, 0.0, "М'ясо"),
    ("Індичка", 189, 29.0, 7.0, 0.0, "М'ясо"),
    ("Лосось", 208, 20.0, 13.0, 0.0, "Риба"),
    ("Тунець", 132, 28.0, 1.0, 0.0, "Риба"),
    ("Тріска", 82, 18.0, 0.7, 0.0, "Риба"),
    ("Скумбрія", 205, 18.0, 13.9, 0.0, "Риба"),
    ("Яйце куряче", 155, 13.0, 11.0, 1.1, "М'ясо"),
    ("Молоко 2.5%", 52, 2.8, 2.5, 4.7, "Молочні продукти"),
    ("Кефір", 40, 3.4, 1.0, 4.1, "Молочні продукти"),
    ("Сир твердий", 350, 25.0, 27.0, 0.0, "Молочні продукти"),
    ("Сир кисломолочний", 98, 18.0, 2.0, 3.3, "Молочні продукти"),
    ("Йогурт натуральний", 60, 4.0, 3.0, 4.5, "Молочні продукти"),
    ("Вершкове масло", 748, 0.8, 82.5, 0.7, "Молочні продукти"),
    ("Рис білий", 130, 2.7, 0.3, 28.0, "Крупи"),
    ("Гречка", 343, 13.0, 3.4, 62.0, "Крупи"),
    ("Вівсянка", 389, 17.0, 7.0, 66.0, "Крупи"),
    ("Пшоно", 378, 11.0, 4.0, 69.0, "Крупи"),
    ("Перловка", 320, 9.0, 1.1, 66.0, "Крупи"),
    ("Макарони", 371, 13.0, 1.5, 75.0, "Крупи"),
    ("Хліб пшеничний", 265, 8.0, 3.2, 49.0, "Хлібобулочні"),
    ("Хліб житній", 214, 6.5, 1.2, 40.0, "Хлібобулочні"),
    ("Батон", 262, 7.5, 2.9, 51.0, "Хлібобулочні"),
    ("Картопля", 77, 2.0, 0.1, 17.0, "Овочі"),
    ("Морква", 41, 0.9, 0.2, 10.0, "Овочі"),
    ("Буряк", 43, 1.6, 0.2, 9.6, "Овочі"),
    ("Цибуля ріпчаста", 40, 1.1, 0.1, 9.3, "Овочі"),
    ("Часник", 149, 6.4, 0.5, 33.0, "Овочі"),
    ("Капуста білокачанна", 25, 1.3, 0.1, 5.8, "Овочі"),
    ("Помідор", 18, 0.9, 0.2, 3.9, "Овочі"),
    ("Огірок", 15, 0.7, 0.1, 3.6, "Овочі"),
    ("Перець солодкий", 27, 1.0, 0.2, 6.0, "Овочі"),
    ("Кабачок", 24, 0.6, 0.3, 4.6, "Овочі"),
    ("Гарбуз", 26, 1.0, 0.1, 6.5, "Овочі"),
    ("Броколі", 34, 2.8, 0.4, 6.6, "Овочі"),
    ("Яблуко", 52, 0.3, 0.2, 14.0, "Фрукти"),
    ("Банан", 96, 1.5, 0.2, 21.0, "Фрукти"),
    ("Апельсин", 43, 0.9, 0.2, 8.1, "Фрукти"),
    ("Груша", 57, 0.4, 0.1, 15.0, "Фрукти"),
    ("Виноград", 65, 0.6, 0.2, 16.0, "Фрукти"),
    ("Лимон", 29, 1.1, 0.3, 9.3, "Фрукти"),
    ("Полуниця", 32, 0.7, 0.3, 7.7, "Фрукти"),
    ("Квасоля", 333, 21.0, 2.0, 54.0, "Бобові"),
    ("Горох", 298, 20.5, 2.0, 49.0, "Бобові"),
    ("Сочевиця", 295, 24.0, 1.1, 46.0, "Бобові"),
    ("Нут", 309, 19.0, 6.0, 46.0, "Бобові"),
    ("Мигдаль", 579, 21.0, 50.0, 22.0, "Горіхи та насіння"),
    ("Волоський горіх", 654, 15.0, 65.0, 14.0, "Горіхи та насіння"),
    ("Насіння соняшника", 584, 21.0, 51.0, 20.0, "Горіхи та насіння"),
    ("Кава чорна", 2, 0.1, 0.0, 0.3, "Напої"),
    ("Чай зелений", 1, 0.0, 0.0, 0.3, "Напої"),
    ("Сік апельсиновий", 45, 0.7, 0.2, 10.0, "Напої"),
]
DISHES = [
    ("Борщ", "Класичний борщ з буряком", [
        ("Буряк", 150), ("Картопля", 200), ("Капуста білокачанна", 100),
        ("Морква", 50), ("Цибуля ріпчаста", 50), ("Яловичина", 150),
    ]),
    ("Плов", "Плов з яловичиною", [
        ("Рис білий", 200), ("Яловичина", 150), ("Морква", 100), ("Цибуля ріпчаста", 50),
    ]),
    ("Грецький салат", "Легкий овочевий салат", [
        ("Помідор", 150), ("Огірок", 100), ("Перець солодкий", 50), ("Сир твердий", 50),
    ]),
    ("Омлет", "Простий сніданок", [
        ("Яйце куряче", 120), ("Молоко 2.5%", 50), ("Сир твердий", 30),
    ]),
    ("Гречка з куркою", "Ситна страва", [
        ("Гречка", 150), ("Куряча грудка", 150),
    ]),
    ("Овочеве рагу", "Тушковані овочі", [
        ("Кабачок", 150), ("Картопля", 150), ("Морква", 80), ("Цибуля ріпчаста", 50), ("Помідор", 100),
    ]),
    ("Фруктовий салат", "Легкий десерт", [
        ("Яблуко", 100), ("Банан", 100), ("Апельсин", 100), ("Виноград", 80),
    ]),
    ("Курячий суп", "Домашній суп", [
        ("Куряча грудка", 200), ("Картопля", 150), ("Морква", 50), ("Цибуля ріпчаста", 30), ("Вермішель", 50),
    ]),
]

def seed_database(request):
    created = {"categories": 0, "products": 0, "dishes": 0, "ingredients": 0}

    with transaction.atomic():
        # 1. Категории
        category_map = {}
        for cat_name in CATEGORIES:
            category, was_created = Category.objects.get_or_create(name=cat_name)
            category_map[cat_name] = category
            if was_created:
                created["categories"] += 1

        # 2. Продукты
        product_map = {}
        for name, kcal, protein, fat, carbs, cat_name in PRODUCTS:
            product, was_created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "calories_per_100g": kcal,
                    "protein_per_100g": protein,
                    "fat_per_100g": fat,
                    "carbs_per_100g": carbs,
                    "category": category_map[cat_name],
                }
            )
            product_map[name] = product
            if was_created:
                created["products"] += 1

        # 3. Блюда + ингредиенты
        for dish_name, description, ingredients in DISHES:
            dish, was_created = Dish.objects.get_or_create(
                name=dish_name,
                defaults={"description": description}
            )
            if was_created:
                created["dishes"] += 1

            for product_name, weight in ingredients:
                product = product_map.get(product_name)
                if product is None:
                    continue  # пропускаем, если продукта нет в списке (например "Вермішель")
                _, ing_created = DishIngredient.objects.get_or_create(
                    dish=dish, product=product,
                    defaults={"weight_grams": weight}
                )
                if ing_created:
                    created["ingredients"] += 1

            # пересчитываем калорийность блюда после добавления ингредиентов
            dish.calories = dish.get_calories()
            dish.save(update_fields=["calories"])

    return HttpResponse(
        f"Готово!<br>"
        f"Категорій створено: {created['categories']}<br>"
        f"Продуктів створено: {created['products']}<br>"
        f"Блюд створено: {created['dishes']}<br>"
        f"Інгредієнтів створено: {created['ingredients']}"
    )