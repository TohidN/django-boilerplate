from django.contrib import admin

from .models import AccountSignup, Profile


@admin.register(AccountSignup)
class AccountSignupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "last_active",
        "activation_key",
        "activation_notification_send",
        "email_unconfirmed",
        "email_confirmation_key",
        "email_confirmation_key_created",
    )
    list_filter = (
        "user",
        "last_active",
        "activation_notification_send",
        "email_confirmation_key_created",
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "avatar_option",
        "avatar",
        "website",
        "bio",
        "language",
        "country",
        "location",
        "public_mail",
        "privacy",
        "notification_setting",
    )
    list_filter = ("user",)
