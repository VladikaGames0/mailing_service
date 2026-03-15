from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


class OwnerRequiredMixin:
    """Миксин для проверки владельца объекта"""

    def dispatch(self, request, *args, **kwargs):
        # Для списковых представлений проверка не нужна
        if hasattr(self, 'get_object'):
            obj = self.get_object()
            # Проверяем права менеджера
            if request.user.has_perm(f'{self.model._meta.app_label}.can_view_all_{self.model._meta.model_name}s'):
                return super().dispatch(request, *args, **kwargs)

            # Проверяем владельца
            if obj.owner != request.user and not request.user.is_superuser:
                raise PermissionDenied("У вас нет прав для доступа к этому объекту")

        return super().dispatch(request, *args, **kwargs)


class OwnerFilterMixin:
    """Миксин для фильтрации queryset по владельцу"""

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Суперадмин и менеджеры видят всё
        if user.is_superuser or user.has_perm(
                f'{self.model._meta.app_label}.can_view_all_{self.model._meta.model_name}s'):
            return queryset

        # Обычные пользователи видят только свои объекты
        return queryset.filter(owner=user)