from django.contrib import admin

from .models import Balance, CustomUser, Subscription


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0


class BalanceInline(admin.StackedInline):
    model = Balance
    extra = 5


class GroupInline(admin.TabularInline):
    model = CustomUser.groups.through
    extra = 0
    verbose_name = 'Группа'
    verbose_name_plural = 'Группы'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Класс для работы с пользователями в админке."""

    list_display = ('id', 'email', 'first_name', 'last_name',)
    fields = ('username', 'first_name', 'last_name', 'email', 'password')
    search_fields = ('email',)
    inlines = (SubscriptionInline, GroupInline, BalanceInline)
    ordering = ('-id',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)
