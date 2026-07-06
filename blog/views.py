from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect

from .forms import RegisterForm
from .models import UserProfile, DiaryEntry
# Create your views here.
def registe_view(request):
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
def profile_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return redirect("profile_create")
    return render(request, "accounts/profile.html", {"profile": profile})
@login_required
def diary_view(request):
    entries = DiaryEntry.objects.filter(user=request.user).order_by("-date")
    return render(request, "diary/diary.html", {"entries": entries})
@login_required
def dairy_add_view(request):
    if request.method == "POST":
        #тут твоя форма DiaryEntryForm — головне: user=request.user ставиться в коді,
        # НІКОЛИ не бери user_id з POST/GET, інакше користувач зможе писати в чужий щоденник
        entry = DiaryEntry(user=request.user)
        entry.save()
        return redirect("diary")
    return render(request, "diary/diary_add.html")

####### Volodymur
