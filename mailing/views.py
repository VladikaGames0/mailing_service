from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from .models import Recipient, Message, Mailing, Attempt


def home(request):
    """Главная страница"""
    # Пробуем получить данные из кеша
    cache_key = 'home_page_stats'
    context = cache.get(cache_key)

    if not context:
        # Если данных нет в кеше, вычисляем
        context = {
            'total_mailings': Mailing.objects.count(),
            'active_mailings': Mailing.objects.filter(
                status='started',
                start_time__lte=timezone.now(),
                end_time__gte=timezone.now()
            ).count(),
            'total_recipients': Recipient.objects.count(),
        }
        # Сохраняем в кеш на 5 минут
        cache.set(cache_key, context, 300)

    return render(request, 'mailing/home.html', context)


# CRUD для получателей
class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailing/recipient_list.html'
    context_object_name = 'recipients'
    paginate_by = 20

    def get_queryset(self):
        """Фильтрация по владельцу"""
        user = self.request.user
        if user.is_superuser:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = 'mailing/recipient_detail.html'
    context_object_name = 'recipient'

    def get_queryset(self):
        """Проверка доступа"""
        user = self.request.user
        if user.is_superuser:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    template_name = 'mailing/recipient_form.html'
    fields = ['email', 'full_name', 'comment']
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Получатель успешно создан')
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    template_name = 'mailing/recipient_form.html'
    fields = ['email', 'full_name', 'comment']
    success_url = reverse_lazy('mailing:recipient_list')

    def get_queryset(self):
        """Только свои получатели"""
        user = self.request.user
        if user.is_superuser:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)

    def form_valid(self, form):
        messages.success(self.request, 'Получатель успешно обновлен')
        return super().form_valid(form)


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'mailing/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def get_queryset(self):
        """Только свои получатели"""
        user = self.request.user
        if user.is_superuser:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)

    def form_valid(self, form):
        messages.success(self.request, 'Получатель успешно удален')
        return super().form_valid(form)


# CRUD для сообщений
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20

    def get_queryset(self):
        """Фильтрация по владельцу"""
        user = self.request.user
        if user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        """Проверка доступа"""
        user = self.request.user
        if user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = 'mailing/message_form.html'
    fields = ['subject', 'body']
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение успешно создано')
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = 'mailing/message_form.html'
    fields = ['subject', 'body']
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        """Только свои сообщения"""
        user = self.request.user
        if user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение успешно обновлено')
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        """Только свои сообщения"""
        user = self.request.user
        if user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение успешно удалено')
        return super().form_valid(form)


# CRUD для рассылок
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'
    paginate_by = 10

    def get_queryset(self):
        """Фильтрация по владельцу и обновление статусов"""
        user = self.request.user
        if user.is_superuser:
            mailings = Mailing.objects.all()
        else:
            mailings = Mailing.objects.filter(owner=user)

        # Обновляем статусы
        for mailing in mailings:
            mailing.update_status()
        return mailings


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        """Проверка доступа"""
        user = self.request.user
        if user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    fields = ['start_time', 'end_time', 'message', 'recipients']
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Фильтруем сообщения и получателей по владельцу
        user = self.request.user
        form.fields['message'].queryset = Message.objects.filter(owner=user)
        form.fields['recipients'].queryset = Recipient.objects.filter(owner=user)
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = 'created'
        messages.success(self.request, 'Рассылка успешно создана')
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    template_name = 'mailing/mailing_form.html'
    fields = ['start_time', 'end_time', 'message', 'recipients']
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        """Только свои рассылки"""
        user = self.request.user
        if user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        form.fields['message'].queryset = Message.objects.filter(owner=user)
        form.fields['recipients'].queryset = Recipient.objects.filter(owner=user)
        return form

    def form_valid(self, form):
        form.instance.update_status()
        messages.success(self.request, 'Рассылка успешно обновлена')
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        """Только свои рассылки"""
        user = self.request.user
        if user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка успешно удалена')
        return super().form_valid(form)


# Запуск рассылки
class MailingStartView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_start.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        """Только свои рассылки"""
        user = self.request.user
        if user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()
        mailing.update_status()

        # Проверяем, можно ли запустить рассылку
        if mailing.status != 'started':
            messages.error(request, 'Рассылку можно запустить только в статусе "Запущена"')
            return redirect('mailing:mailing_detail', pk=mailing.pk)

        # Отправляем письма
        success_count = 0
        fail_count = 0

        for recipient in mailing.recipients.all():
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
            except Exception as e:
                Attempt.objects.create(
                    mailing=mailing,
                    status='failed',
                    server_response=str(e)[:200]
                )
                fail_count += 1

        messages.success(
            request,
            f'Рассылка завершена. Успешно: {success_count}, Ошибок: {fail_count}'
        )
        return redirect('mailing:mailing_detail', pk=mailing.pk)


# Просмотр попыток рассылок
class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = 'mailing/attempt_list.html'
    context_object_name = 'attempts'
    paginate_by = 30

    def get_queryset(self):
        """Показываем попытки только своих рассылок"""
        user = self.request.user
        if user.is_superuser:
            return Attempt.objects.all()
        return Attempt.objects.filter(mailing__owner=user)