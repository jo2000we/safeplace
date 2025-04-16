from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Teacher, TimeSlot


class TeacherAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('gender',)}),
    )
    # Das Feld "gender" auch beim Anlegen eines neuen Users anzeigen:
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('gender',)}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'gender', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'gender')
    search_fields = ('username', 'first_name', 'last_name', 'email')


admin.site.register(Teacher, TeacherAdmin)
admin.site.register(TimeSlot)
