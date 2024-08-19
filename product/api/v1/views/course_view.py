from api.v1.permissions import (IsStudentOrIsAdmin, ReadOnlyOrIsAdmin,
                                make_payment)
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import CustomUser, Subscription


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы."""

    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Список курсов, на которые подписан пользователь."""

        user: CustomUser = request.user
        serializer = SubscriptionSerializer(user.subscriptions.all(), many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def buy(self, request):
        """
        Список курсов, доступных для покупки (они еще
        не куплены пользователем).
        """

        user: CustomUser = request.user

        # Получение списка курсов, на которые пользователь уже подписан
        subscribed_courses = user.subscriptions.values_list('course', flat=True)

        # Получение списка курсов, доступных для покупки
        available_courses = Course.objects.exclude(id__in=subscribed_courses)

        # Сериализация списка курсов
        serializer = CourseSerializer(available_courses, many=True)

        return Response(serializer.data)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""

        course = get_object_or_404(Course, id=pk)
        user: CustomUser = request.user

        # Проверка, подписан ли пользователь уже на этот курс
        if course.has_access(user):
            return Response(
                data={'error': 'Вы уже подписаны на этот курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            make_payment(user, course)
        except ValueError as e:
            return Response(
                data={'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создание объекта Subscription для связи пользователя с курсом
        Subscription.objects.create(user=user, course=course)

        return Response(
            data={'success': 'Доступ к курсу куплен.'},
            status=status.HTTP_201_CREATED
        )
