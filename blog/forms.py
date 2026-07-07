from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import DiaryEntry, Category, Product, Dish, DishIngredient

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class DiaryEntryForm(forms.ModelForm):
    """Форма додавання запису в щоденник.
    ВАЖЛИВО: поле 'user' навмисно НЕМАЄ у fields — власника ставить view
    з request.user (form.save(commit=False) -> instance.user = request.user),
    інакше можна підсунути чужий user_id через приховане поле форми.
    """

    class Meta:
        model = DiaryEntry
        fields = ["date", "product", "dish", "amount_grams"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        dish = cleaned_data.get("dish")

        if not product and not dish:
            raise forms.ValidationError("Оберіть продукт або страву.")
        if product and dish:
            raise forms.ValidationError("Оберіть щось одне: або продукт, або страву.")

        return cleaned_data
    
# Volodymur

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "calories_per_100g", "category"
                 ,"protein_per_100g", "fat_per_100g",
                 "carbs_per_100g"]
    
class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ["name", "description", "calories"]
        
class DishIngredientsForm(forms.ModelForm):
    class Meta:
        model = DishIngredient
        fields = ["product", "weight_grams"]
        
DishIngredientFormSet = forms.inlineformset_factory(
    Dish,
    DishIngredient,
    form=DishIngredientsForm,
    extra=3,
    can_delete=True
)