from django.urls import path
from . import views

app_name = 'mailing'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),

    # CRUD для получателей
    path('recipients/', views.RecipientListView.as_view(), name='recipient_list'),
    path('recipients/<int:pk>/', views.RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipients/create/', views.RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/update/', views.RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/<int:pk>/delete/', views.RecipientDeleteView.as_view(), name='recipient_delete'),

    # CRUD для сообщений
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/', views.MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),

    # CRUD для рассылок
    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    path('mailings/<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/update/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),

    # Запуск рассылки
    path('mailings/<int:pk>/start/', views.MailingStartView.as_view(), name='mailing_start'),

    # Попытки рассылок
    path('attempts/', views.AttemptListView.as_view(), name='attempt_list'),
]