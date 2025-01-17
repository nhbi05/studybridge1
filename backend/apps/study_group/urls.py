from django.urls import path
from .views import (
    StudyGroupViewSet,
    GroupMembershipViewSet,
    GroupResourceViewSet,
    GroupDiscussionViewSet,
    DiscussionCommentViewSet,
)

urlpatterns = [
    # StudyGroup URLs
    path('study-groups/', StudyGroupViewSet.as_view({'get': 'list', 'post': 'create'}), name='study-group-list'),
    path('study-groups/<int:pk>/', StudyGroupViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='study-group-detail'),
    path('study-groups/<int:pk>/members/', StudyGroupViewSet.as_view({'get': 'members'}), name='study-group-members'),

    # GroupMembership URLs
    path('memberships/', GroupMembershipViewSet.as_view({'get': 'list', 'post': 'create'}), name='membership-list'),
    path('memberships/<int:pk>/', GroupMembershipViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='membership-detail'),

    # GroupResource URLs
    path('group-resources/', GroupResourceViewSet.as_view({'get': 'list', 'post': 'create'}), name='group-resource-list'),
    path('group-resources/<int:pk>/', GroupResourceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='group-resource-detail'),

    # GroupDiscussion URLs
    path('discussions/', GroupDiscussionViewSet.as_view({'get': 'list', 'post': 'create'}), name='discussion-list'),
    path('discussions/<int:pk>/', GroupDiscussionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='discussion-detail'),
    path('discussions/<int:pk>/comments/', GroupDiscussionViewSet.as_view({'get': 'comments'}), name='discussion-comments'),

    # DiscussionComment URLs
    path('comments/', DiscussionCommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='comment-list'),
    path('comments/<int:pk>/', DiscussionCommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='comment-detail'),
]
