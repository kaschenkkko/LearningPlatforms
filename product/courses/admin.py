from django.contrib import admin

from .models import Course, Group, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Класс для работы с курсами в админке."""

    list_display = ('id', 'author', 'title', 'start_date',)
    fields = ('author', 'title', 'start_date', 'price',)
    search_fields = ('title',)
    ordering = ('-id',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Класс для работы с уроками в админке."""

    list_display = ('id', 'course', 'title',)
    fields = ('course', 'title', 'link')
    search_fields = ('title',)
    list_filter = ('course',)
    ordering = ('-id',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Класс для работы с группами в админке."""

    list_display = ('id', 'course', 'title',)
    fields = ('course', 'title',)
    search_fields = ('title',)
    list_filter = ('course',)
    ordering = ('-id',)
