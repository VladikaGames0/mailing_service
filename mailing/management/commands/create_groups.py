from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Mailing, Message, Recipient


class Command(BaseCommand):
    help = 'Создание группы менеджеров'

    def handle(self, *args, **options):
        # Создаем группу
        group, created = Group.objects.get_or_create(name='Менеджеры')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана'))
        else:
            self.stdout.write('Группа "Менеджеры" уже существует')
            # Очищаем старые права
            group.permissions.clear()

        # Получаем все права для наших моделей
        permissions = Permission.objects.filter(
            content_type__in=[
                ContentType.objects.get_for_model(Mailing),
                ContentType.objects.get_for_model(Message),
                ContentType.objects.get_for_model(Recipient),
            ]
        )

        # Добавляем права группе
        group.permissions.set(permissions)

        self.stdout.write(
            self.style.SUCCESS(f'Добавлено {permissions.count()} прав для группы "Менеджеры"')
        )