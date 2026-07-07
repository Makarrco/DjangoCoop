from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import RegisterForm, ProfileForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("profile_create")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})
@login_required
def profile_create_view(request):
    if hasattr(request.user, "profile"):
        return redirect("profile")
    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("profile")
        # ВАЖЛИВО: якщо форма невалідна — НЕ створюй нову пусту форму,
        # рендери саме `form` з помилками, інакше юзер не бачить, що не так.
    else:
        form = ProfileForm()

    return render(request, "accounts/profile_form.html", {"form": form})