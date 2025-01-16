from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    BarangayDocument,
    Requirement,
    Schedule,
    Email,
    UserProfile,
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "firstname",
        "lastname",
        "birthday",
        "email",
        "is_staff",
        "is_active",
        "last_login",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active")
    ordering = ("email",)
    search_fields = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("firstname", "lastname", "birthday")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    list_display_links = ("email",)
    readonly_fields = ["last_login", "date_joined"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "firstname",
                    "lastname",
                    "birthday",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    inlines = [UserProfileInline]


class RequirementInline(admin.TabularInline):
    model = BarangayDocument.requirements.through
    extra = 1


class BarangayDocumentAdmin(admin.ModelAdmin):
    # model = BarangayDocument
    list_display = ("name", "description")
    search_fields = ("name",)
    list_filter = ("requirements",)
    exclude = ("requirements",)
    inlines = [RequirementInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        form.save_m2m()

    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('name', 'description', 'requirements')
    #     })
    # )


class RequirementAdmin(admin.ModelAdmin):
    model = Requirement
    list_display = ("name",)
    search_fields = ("name",)

    add_fieldsets = (None, {"classes": ("wide",), "fields": ("name",)})


class ScheduleAdmin(admin.ModelAdmin):
    model = Schedule
    list_display = ("purpose", "date", "timeslot", "user", "status")
    search_fields = ("user", "date", "purpose", "status")

    add_fields = (
        None,
        {
            "classes": ("wide",),
            "fields": ("purpose", "date", "timeslot", "user", "status"),
        },
    )


class EmailAdmin(admin.ModelAdmin):
    model = Email
    list_display = ("type", "subject", "message", "date_created")
    search_fields = ("type", "subject")

    add_fields = (
        None,
        {"classes": ("wide",), "fields": ("type", "subject", "message")},
    )


admin.site.register(Email, EmailAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BarangayDocument, BarangayDocumentAdmin)
admin.site.register(Requirement, RequirementAdmin)
admin.site.register(Schedule, ScheduleAdmin)
# admin.site.unregister(BarangayDocument.requirements.through)
