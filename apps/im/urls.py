from django.urls import path

from . import views

urlpatterns = [
    path("conversations/", views.ConversationListView.as_view(), name="conversation-list"),
    path("conversation/", views.ConversationView.as_view(), name="conversation-create"),
    path("conversation/<uuid:conversation_id>/", views.ConversationDetailView.as_view(), name="conversation-detail"),
    path("conversation/<uuid:conversation_id>/messages/", views.MessageHistoryView.as_view(), name="message-history"),
    path("messages/<uuid:message_id>/read/", views.MarkAsReadView.as_view(), name="mark-as-read"),
    path(
        "conversations/<uuid:conversation_id>/read/",
        views.MarkConversationAsReadView.as_view(),
        name="mark-conversation-as-read",
    ),
    path("unread/", views.UnreadCountView.as_view(), name="unread-count"),
    path("unread/<uuid:conversation_id>/", views.UnreadCountView.as_view(), name="unread-count-conversation"),
]
