from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import StudyGroup, GroupMembership, GroupResource, GroupDiscussion, DiscussionComment
from .serializers import (
    StudyGroupSerializer,
    GroupMembershipSerializer,
    GroupResourceSerializer,
    GroupDiscussionSerializer,
    DiscussionCommentSerializer,
)
# Create your views here.
class StudyGroupViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for study groups.
    """
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Retrieve all members of a study group."""
        group = self.get_object()
        members = group.members.all()
        serializer = GroupMembershipSerializer(members, many=True)
        return Response(serializer.data)

class GroupMembershipViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for group memberships.
    """
    queryset = GroupMembership.objects.all()
    serializer_class = GroupMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GroupResourceViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for group resources.
    """
    queryset = GroupResource.objects.all()
    serializer_class = GroupResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

class GroupDiscussionViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for group discussions.
    """
    queryset = GroupDiscussion.objects.all()
    serializer_class = GroupDiscussionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Retrieve all comments in a discussion."""
        discussion = self.get_object()
        comments = discussion.discussioncomment_set.all()
        serializer = DiscussionCommentSerializer(comments, many=True)
        return Response(serializer.data)

class DiscussionCommentViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for discussion comments.
    """
    queryset = DiscussionComment.objects.all()
    serializer_class = DiscussionCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
