from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .forms import (
    EditAccountForm,
    EditProfileForm,
    EditSettingsForm,
    SignupForm,
    SinginForm,
)
from .models import AccountSignup, Profile
from .settings import LOGIN_REDIRECT_URL, REMEMBER_ME_DAYS


def profile_list(request):
    users = User.objects.all()

    page = request.GET.get("page", 1)
    paginator = Paginator(users, 20)
    adjacent_pages = 5
    page = int(page)
    start_page = max(page - adjacent_pages, 1)
    if start_page <= 3:
        start_page = 1
    end_page = page + adjacent_pages + 1
    if end_page >= paginator.num_pages - 1:
        end_page = page + 1
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    context = {
        "users": users,
        "paginator_range": range(start_page, end_page),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "profile-list.html", context)


def profile(request, username):
    user = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user)

    context = {
        "user": user,
        "profile": user_profile,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    if user_profile.privacy=="o" or request.user.username==username or request.user.is_superuser is True:
        return render(request, "profile.html", context)
    return render(request, "profile-private.html", context)


def account_edit(request, username):
    """
    Account Form
    """
    if request.user.is_superuser is not True and request.user.username != username:
        return render(request, "profile-no-permission.html")

    user = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user)
    form = EditAccountForm(instance=user)

    if request.method == "POST":
        form = EditAccountForm(request.POST or None, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse("account:profile", args=[user.username])
            )

    context = {
        "user": user,
        "profile": user_profile,
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "profile-account-edit.html", context)


def profile_edit(request, username):
    """
    Profile Form
    """
    if request.user.is_superuser is not True and request.user.username != username:
        return render(request, "profile-no-permission.html")

    user = User.objects.get(username=username)
    user_profile = Profile.objects.get(user=user)
    form = EditProfileForm(instance=user_profile)

    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
    context = {
        "user": user,
        "profile": user_profile,
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "profile-edit.html", context)


def settings_edit(request, username):
    """
    Edit account settings
    """
    if request.user.is_superuser is not True and request.user.username != username:
        return render(request, "profile-no-permission.html")

    user = User.objects.get(username=username)
    user_profile, created = Profile.objects.get_or_create(user=user)

    form = EditSettingsForm(request.POST or None, instance=user_profile)

    if request.method == "POST":
        if form.is_valid():
            form.save()

    context = {
        "user": user,
        "profile": user_profile,
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "profile-settings-edit.html", context)


def signup(request):
    """
    Signup of an account.
    1. Signup with username, email and password
    2. get confirmation email with an activation link
    3. redirect user to homepage or visiting page
    """
    form = SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            redirect_url = "/"
            return redirect(redirect_url)

    context = {
        "form": form,
        "title": _("Sign Up"),
        "url": reverse("account:signup"),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "signup-form.html", context)


def signin(request):
    """
    login of an account.
    1. Signup with (username or email) and password
    2. redirect
    """
    form = SinginForm()
    if request.method == "POST":
        form = SinginForm(request.POST, request.FILES)
        if form.is_valid():
            identification, password, remember_me = (
                form.cleaned_data["identification"],
                form.cleaned_data["password"],
                form.cleaned_data["remember_me"],
            )
            user = authenticate(username=identification, password=password)
            next_path = request.GET.get("next", None) or request.POST.get("next", None)
            if user.is_active:
                if next_path is not None:
                    if next_path:
                        redirect_url = next_path
                    else:
                        redirect_url = LOGIN_REDIRECT_URL
                else:
                    referer = request.META.get("HTTP_REFERER", "").rstrip("/")
                    if referer and not referer.endswith("login"):
                        redirect_url = referer
                    else:
                        redirect_url = "/"
                login(request, user)
                if remember_me:
                    request.session.set_expiry(REMEMBER_ME_DAYS * 86400)
                else:
                    request.session.set_expiry(0)

                # Whereto now?
                return HttpResponseRedirect(redirect_url)
            else:
                # TODO: add message to show user that he is inactive
                return redirect(LOGIN_REDIRECT_URL)

    context = {
        "form": form,
        "title": _("Sign In"),
        "url": reverse("account:signin"),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "signin-form.html", context)


def signout(request, next_page):
    """
    Signs out the user
    """
    logout(request)
    request.session.flush()
    referer = request.META.get("HTTP_REFERER", "").rstrip("/")
    if not next_page:
        if referer and not referer.endswith("login"):
            redirect_url = referer
        else:
            redirect_url = "/"
        return HttpResponseRedirect(redirect_url)
    else:
        return HttpResponseRedirect(next_page)


def activate(request, activation_key):
    """
    Activate a user with an activation key.

    The key is a SHA1 string. When the SHA1 is found with an
    :class:`AccountSignup`, the :class:`User` of that account will be activated.
    After a successful activation the view will redirect to ``success_url``.
    If the SHA1 is not found, the user will be shown the ``failed_url`` template displaying a fail message.
    If the SHA1 is found but expired, ``retry_template`` is used instead so user can get a new activation key.
    """
    try:
        if not AccountSignup.objects.check_expired_activation(activation_key):
            user = AccountSignup.objects.activate_user(activation_key)
            if user:
                # Sign the user in.
                User = get_user_model()
                this_user = User.objects.get(email__iexact=user.email)
                this_user.backend = "django.contrib.auth.backends.ModelBackend"
                login(request, user=this_user)
                redirect_to = reverse(
                    "account:profile", kwargs={"username": user.username}
                )
                return redirect(redirect_to)
            else:
                return render(request, "activate_fail.html")
        else:
            context = {
                "activation_key": activation_key,
            }
            return render(request, "activate_retry.html", context)

    except AccountSignup.DoesNotExist:
        return render(request, "activate_fail.html")


def activate_retry(request, activation_key):
    """
    Reissue a new ``activation_key`` for the user with the expired ``activation_key``.
    """
    try:
        if AccountSignup.objects.check_expired_activation(activation_key):
            new_key = AccountSignup.objects.reissue_activation(activation_key)
            if new_key:
                return render(request, "activate_retry_success.html")
            else:
                return redirect(reverse("account:activate", args=(activation_key,)))
        else:
            return redirect(reverse("account:activate", args=(activation_key,)))
    except AccountSignup.DoesNotExist:
        return redirect(reverse("account:activate", args=(activation_key,)))
