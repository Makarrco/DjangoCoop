from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import ProfileForm, DiaryEntryForm
from .models import UserProfile, DiaryEntry


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
    """Список записів ЛИШЕ поточного користувача + підсумки за день."""
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
