from courses.models import Course
from django.shortcuts import get_object_or_404
from rest_framework.permissions import SAFE_METHODS, BasePermission
from users.models import Subscription


def make_payment(user, course):
    """Списание денег и бонусов с баланса пользователя."""

    # Проверка наличия достаточного количества денег на балансе
    if user.balance.total_amount() < course.price:
        raise ValueError('Недостаточно средств на балансе.')

    # Списание денег и бонусов с баланса пользователя
    if course.price > user.balance.bonus:
        user.balance.money -= (course.price - user.balance.bonus)
        user.balance.bonus = 0
    else:
        user.balance.bonus -= course.price
    user.balance.save()


class IsStudentOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        course_id = view.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        return request.user.is_staff or (
            request.method in SAFE_METHODS and
            Subscription.objects.filter(user=request.user, course=course).exists()
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or (
            request.method in SAFE_METHODS and
            Subscription.objects.filter(user=request.user, course=obj.course).exists()
        )


class ReadOnlyOrIsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.method in SAFE_METHODS
