from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, BarangayDocument, Requirement, Schedule


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('firstname', 'lastname', 'birthday', 'email', 'is_staff', 'is_active', 'last_login', 'date_joined')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('firstname', 'lastname', 'birthday')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display_links = ('email',)
    readonly_fields = ['last_login', 'date_joined']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('firstname', 'lastname', 'birthday', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )


class BarangayDocumentAdmin(admin.ModelAdmin):
    model = BarangayDocument
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('requirements',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'description', 'requirements')
        })
    )


class RequirementAdmin(admin.ModelAdmin):
    model = Requirement
    list_display = ('name',)
    search_fields = ('name',)

    add_fieldsets = (
        None, {
            'classes': ('wide',),
            'fields': ('name',)
        }
    )


class ScheduleAdmin(admin.ModelAdmin):
    model = Schedule
    list_display = ('purpose', 'date', 'timeslot', 'user', 'status')
    search_fields = ('user', 'date', 'purpose', 'status')

    add_fields = (
        None, {
            'classes': ('wide',),
            'fields': ('purpose', 'date', 'timeslot', 'user', 'status'),
        }
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(BarangayDocument, BarangayDocumentAdmin)
admin.site.register(Requirement, RequirementAdmin)
admin.site.register(Schedule, ScheduleAdmin)