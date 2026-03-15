from django.contrib import admin
from .models import Recipient, Message, Mailing, Attempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email')
    search_fields = ('full_name', 'email')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject',)
    search_fields = ('subject',)


class AttemptInline(admin.TabularInline):
    model = Attempt
    extra = 0
    readonly_fields = ('attempt_time', 'status', 'server_response')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'start_time', 'end_time', 'status')
    list_filter = ('status',)
    search_fields = ('message__subject',)
    inlines = [AttemptInline]
    readonly_fields = ('status',)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'mailing', 'attempt_time', 'status')
    list_filter = ('status',)
    readonly_fields = ('attempt_time',)