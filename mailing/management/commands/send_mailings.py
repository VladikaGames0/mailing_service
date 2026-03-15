from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from mailing.models import Mailing, Attempt


class Command(BaseCommand):
    help = 'Отправка запланированных рассылок'

    def add_arguments(self, parser):
        parser.add_argument('--mailing_id', type=int, help='ID конкретной рассылки для отправки')

    def handle(self, *args, **options):
        mailing_id = options.get('mailing_id')

        if mailing_id:
            # Отправляем конкретную рассылку
            try:
                mailings = [Mailing.objects.get(id=mailing_id)]
            except Mailing.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Рассылка с ID {mailing_id} не найдена'))
                return
        else:
            # Отправляем все активные рассылки
            mailings = Mailing.objects.filter(
                status='started',
                start_time__lte=timezone.now(),
                end_time__gte=timezone.now()
            )

        if not mailings:
            self.stdout.write(self.style.WARNING('Нет рассылок для отправки'))
            return

        for mailing in mailings:
            self.stdout.write(f'Обработка рассылки #{mailing.id} - {mailing.message.subject}')

            # Проверяем статус
            mailing.update_status()
            if mailing.status != 'started':
                self.stdout.write(self.style.WARNING(f'Рассылка #{mailing.id} не активна'))
                continue

            # Отправляем письма
            success_count = 0
            fail_count = 0
            total = mailing.recipients.count()

            self.stdout.write(f'Всего получателей: {total}')

            for i, recipient in enumerate(mailing.recipients.all(), 1):
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body,
                        from_email='noreply@mailingservice.com',
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )
                    Attempt.objects.create(
                        mailing=mailing,
                        status='success',
                        server_response='OK'
                    )
                    success_count += 1
                    self.stdout.write(f'  [{i}/{total}] ✓ {recipient.email}')
                except Exception as e:
                    Attempt.objects.create(
                        mailing=mailing,
                        status='failed',
                        server_response=str(e)[:200]
                    )
                    fail_count += 1
                    self.stdout.write(self.style.ERROR(f'  [{i}/{total}] ✗ {recipient.email}: {str(e)[:50]}'))

            self.stdout.write(
                self.style.SUCCESS(
                    f'Рассылка #{mailing.id} завершена. '
                    f'Успешно: {success_count}, Ошибок: {fail_count}'
                )
            )