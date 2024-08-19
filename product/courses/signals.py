from courses.models import Group
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from users.models import Subscription


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """Распределение нового студента в группу курса."""

    if created:
        course = instance.course
        groups = course.groups.all()

        if not groups:
            Group.objects.create(course=course, title=f'{course.title}-1')
            groups = course.groups.all()

        students = course.subscriptions.values_list('user', flat=True)
        students_per_group = len(students) // len(groups)

        for i, group in enumerate(groups):
            start = i * students_per_group
            end = start + students_per_group
            if i == len(groups) - 1:
                end = None
            group_students = students[start:end]
            group.students.add(*group_students)


@receiver(post_delete, sender=Subscription)
def post_delete_subscription(sender, instance: Subscription, **kwargs):
    """Удаление студента из группы курса при отписке от курса."""

    course = instance.course
    user = instance.user
    group = course.groups.get(students=user)
    group.students.remove(user)
