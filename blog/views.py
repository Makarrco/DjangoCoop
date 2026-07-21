from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .forms import ProfileForm, DiaryEntryForm, SearchForm
from .models import UserProfile, DiaryEntry, Dish, DishIngredient, Product, Category

from django.http import HttpResponse
from django.db import transaction
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .serializers import ProductSerializer, DishSerializer, DiaryEntrySerializer
from rest_framework import status
from datetime import datetime

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
    entries = DiaryEntry.objects.filter(
        user=request.user
    ).select_related("product", "dish")
    q = request.GET.get("q")
    if q:
        entries = entries.filter(
            Q(product__name__icontains=q) |
            Q(dish__name__icontains=q) |
            Q(date__icontains=q)
        )
    daily_totals = {}
    for entry in entries:
        daily_totals.setdefault(entry.date, 0)
        daily_totals[entry.date] += entry.calories
    norm = None
    if hasattr(request.user, "profile"):
        norm = request.user.profile.calculate_daily_norm()

    return render(
        request,
        "diary/diary.html",
        {
            "entries": entries,
            "daily_totals": daily_totals,
            "norm": norm,
        },
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
    """The `user=request.user` filter ensures that you cannot delete someone else's record,
    even if you substitute someone else's pk in the URL."""
    entry = get_object_or_404(DiaryEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        return redirect("diary")
    return render(request, "diary/diary_confirm_delete.html", {"entry": entry})


####### Volodymur

# @login_required
def search_panel(request):
    form = SearchForm(request.GET)
    products = Product.objects.none()
    dishes = Dish.objects.none()
    query = ""
    category_id = ""
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
            category_id = category.id
            products = products.filter(category__name__icontains=category)
            dishes = dishes.filter(ingridients__category__name__icontains=category).distinct()
    prod_paginator = Paginator(products, 5)
    dish_paginator = Paginator(dishes, 5)
    page_prod_number = request.GET.get("prod_page")
    page_dish_number = request.GET.get("dish_page")
    prod_page_obj = prod_paginator.get_page(page_prod_number)
    dish_page_obj = dish_paginator.get_page(page_dish_number)
    
    if request.headers.get("HX-Request"):
        template = "searchpanel/search.html"
    else:
        template = "searchpanel/searchmain.html"
    
    return render(request, template, {
        "form": form,
        "query": query,
        "category_id": category_id,
        "prod_pag": prod_page_obj,
        "dish_pag": dish_page_obj,
    })

def dish_detail(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    return render(request, "searchpanel/dish_detail.html", {"data": dish})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "searchpanel/product_detail.html", {"data": product})

def error(request, rest):
    return render(request, "404.html")


CATEGORIES = [
    "Vegetables", "Fruits", "Meat", "Fish", "Dairy Products",
    "Grains", "Bakery", "Nuts and Seeds", "Legumes", "Beverages",
]
PRODUCTS = [
    ("Chicken breast", 165, 31.0, 3.6, 0.0, "Meat"),
    ("Beef", 250, 26.0, 15.0, 0.0, "Meat"),
    ("Pork", 242, 27.0, 14.0, 0.0, "Meat"),
    ("Turkey", 189, 29.0, 7.0, 0.0, "Meat"),
    ("Salmon", 208, 20.0, 13.0, 0.0, "Fish"),
    ("Tuna", 132, 28.0, 1.0, 0.0, "Fish"),
    ("Cod", 82, 18.0, 0.7, 0.0, "Fish"),
    ("Mackerel", 205, 18.0, 13.9, 0.0, "Fish"),
    ("Chicken egg", 155, 13.0, 11.0, 1.1, "Meat"),
    ("Milk 2.5%", 52, 2.8, 2.5, 4.7, "Dairy Products"),
    ("Kefir", 40, 3.4, 1.0, 4.1, "Dairy Products"),
    ("Hard cheese", 350, 25.0, 27.0, 0.0, "Dairy Products"),
    ("Cottage cheese", 98, 18.0, 2.0, 3.3, "Dairy Products"),
    ("Natural yogurt", 60, 4.0, 3.0, 4.5, "Dairy Products"),
    ("Butter", 748, 0.8, 82.5, 0.7, "Dairy Products"),
    ("White rice", 130, 2.7, 0.3, 28.0, "Grains"),
    ("Buckwheat", 343, 13.0, 3.4, 62.0, "Grains"),
    ("Oatmeal", 389, 17.0, 7.0, 66.0, "Grains"),
    ("Millet", 378, 11.0, 4.0, 69.0, "Grains"),
    ("Pearl barley", 320, 9.0, 1.1, 66.0, "Grains"),
    ("Pasta", 371, 13.0, 1.5, 75.0, "Grains"),
    ("Wheat bread", 265, 8.0, 3.2, 49.0, "Bakery"),
    ("Rye bread", 214, 6.5, 1.2, 40.0, "Bakery"),
    ("White loaf", 262, 7.5, 2.9, 51.0, "Bakery"),
    ("Potato", 77, 2.0, 0.1, 17.0, "Vegetables"),
    ("Carrot", 41, 0.9, 0.2, 10.0, "Vegetables"),
    ("Beet", 43, 1.6, 0.2, 9.6, "Vegetables"),
    ("Onion", 40, 1.1, 0.1, 9.3, "Vegetables"),
    ("Garlic", 149, 6.4, 0.5, 33.0, "Vegetables"),
    ("White cabbage", 25, 1.3, 0.1, 5.8, "Vegetables"),
    ("Tomato", 18, 0.9, 0.2, 3.9, "Vegetables"),
    ("Cucumber", 15, 0.7, 0.1, 3.6, "Vegetables"),
    ("Bell pepper", 27, 1.0, 0.2, 6.0, "Vegetables"),
    ("Zucchini", 24, 0.6, 0.3, 4.6, "Vegetables"),
    ("Pumpkin", 26, 1.0, 0.1, 6.5, "Vegetables"),
    ("Broccoli", 34, 2.8, 0.4, 6.6, "Vegetables"),
    ("Apple", 52, 0.3, 0.2, 14.0, "Fruits"),
    ("Banana", 96, 1.5, 0.2, 21.0, "Fruits"),
    ("Orange", 43, 0.9, 0.2, 8.1, "Fruits"),
    ("Pear", 57, 0.4, 0.1, 15.0, "Fruits"),
    ("Grapes", 65, 0.6, 0.2, 16.0, "Fruits"),
    ("Lemon", 29, 1.1, 0.3, 9.3, "Fruits"),
    ("Strawberry", 32, 0.7, 0.3, 7.7, "Fruits"),
    ("Beans", 333, 21.0, 2.0, 54.0, "Legumes"),
    ("Peas", 298, 20.5, 2.0, 49.0, "Legumes"),
    ("Lentils", 295, 24.0, 1.1, 46.0, "Legumes"),
    ("Chickpeas", 309, 19.0, 6.0, 46.0, "Legumes"),
    ("Almonds", 579, 21.0, 50.0, 22.0, "Nuts and Seeds"),
    ("Walnut", 654, 15.0, 65.0, 14.0, "Nuts and Seeds"),
    ("Sunflower seeds", 584, 21.0, 51.0, 20.0, "Nuts and Seeds"),
    ("Black coffee", 2, 0.1, 0.0, 0.3, "Beverages"),
    ("Green tea", 1, 0.0, 0.0, 0.3, "Beverages"),
    ("Orange juice", 45, 0.7, 0.2, 10.0, "Beverages"),
]
DISHES = [
    ("Borscht", "Classic beet borscht", [
        ("Beet", 150), ("Potato", 200), ("White cabbage", 100),
        ("Carrot", 50), ("Onion", 50), ("Beef", 150),
    ]),
    ("Pilaf", "Pilaf with beef", [
        ("White rice", 200), ("Beef", 150), ("Carrot", 100), ("Onion", 50),
    ]),
    ("Greek salad", "Light vegetable salad", [
        ("Tomato", 150), ("Cucumber", 100), ("Bell pepper", 50), ("Hard cheese", 50),
    ]),
    ("Omelet", "Simple breakfast", [
        ("Chicken egg", 120), ("Milk 2.5%", 50), ("Hard cheese", 30),
    ]),
    ("Buckwheat with chicken", "Hearty dish", [
        ("Buckwheat", 150), ("Chicken breast", 150),
    ]),
    ("Vegetable stew", "Stewed vegetables", [
        ("Zucchini", 150), ("Potato", 150), ("Carrot", 80), ("Onion", 50), ("Tomato", 100),
    ]),
    ("Fruit salad", "Light dessert", [
        ("Apple", 100), ("Banana", 100), ("Orange", 100), ("Grapes", 80),
    ]),
    ("Chicken soup", "Homemade soup", [
        ("Chicken breast", 200), ("Potato", 150), ("Carrot", 50), ("Onion", 30), ("Vermicelli", 50),
    ]),
]

def seed_database(request):
    created = {"categories": 0, "products": 0, "dishes": 0, "ingredients": 0}
 
    with transaction.atomic():
        # 0. Wipe existing data first (order matters: children before parents)
        DishIngredient.objects.all().delete()
        Dish.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
 
        # 1. Categories
        category_map = {}
        for cat_name in CATEGORIES:
            category, was_created = Category.objects.get_or_create(name=cat_name)
            category_map[cat_name] = category
            if was_created:
                created["categories"] += 1
 
        # 2. Products
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
 
        # 3. Dishes + ingredients
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
                    continue  # skip if product isn't in the list (e.g. "Vermicelli")
                _, ing_created = DishIngredient.objects.get_or_create(
                    dish=dish, product=product,
                    defaults={"weight_grams": weight}
                )
                if ing_created:
                    created["ingredients"] += 1
 
            # recalculate dish calories after adding ingredients
            dish.calories = dish.get_calories()
            dish.save(update_fields=["calories"])
 
    return HttpResponse(
        f"Done!<br>"
        f"Categories created: {created['categories']}<br>"
        f"Products created: {created['products']}<br>"
        f"Dishes created: {created['dishes']}<br>"
        f"Ingredients created: {created['ingredients']}"
    )

    
# REST API

@api_view(["GET"])
def products(request):
    products = Product.objects.all()
    
    q = request.GET.get("q")
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(category__name__icontains=q)
        )
    
    paginator = PageNumberPagination()
    paginator.page_size = 5
    
    paginated_products = paginator.paginate_queryset(products, request)
    
    ps = ProductSerializer(paginated_products, many=True)
    return Response(ps.data)

@api_view(["GET"])
def api_product_detail(request, id):
    products =get_object_or_404(Product, id=id)
    
    ps = ProductSerializer(products)
    return Response(ps.data)

@api_view(["GET"])
def dishes(request):
    dishes = Dish.objects.all()
    
    paginator = PageNumberPagination()
    paginator.page_size = 5
    
    paginated_dishes = paginator.paginate_queryset(dishes, request)
    
    ds = DishSerializer(paginated_dishes, many=True)
    
    return Response(ds.data)

@api_view(["GET"])
def get_entries(request):
    date = request.GET.get("date")
    entries = DiaryEntry.objects.all()
    
    if not date:
        ds = DiaryEntrySerializer(entries, many=True)
        return Response(ds.data)
    
    try:
        parsed_date = datetime.strptime(date, "%d.%m.%Y").date()
    except ValueError:
        return Response(
            {"error": "Waiting for DD.MM.YYYY"},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    entries = entries.filter(date=parsed_date, user=request.user)
    
    ds = DiaryEntrySerializer(entries, many=True)
    return Response(ds.data)

@api_view(["POST"])
def create_entry(request):
    es = DiaryEntrySerializer(data=request.data)
    if es.is_valid():
        es.save(user=request.user)
        return Response(es.data)
    return Response(es.errors)