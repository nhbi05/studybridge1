from rest_framework import serializers
from .models import StudyGroup, GroupMembership, GroupResource, GroupDiscussion, DiscussionComment

class StudyGroupSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()  # Display user string (username)
    members_count = serializers.IntegerField(source='members.count', read_only=True)  # Count members in the group

    class Meta:
        model = StudyGroup
        fields = [
            'id', 'name', 'description', 'course', 'year_of_study', 'semester',
            'subject', 'created_by', 'members_count', 'is_private', 'max_members', 'created_at'
        ]

class GroupMembershipSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Display user string (username)
    group = serializers.StringRelatedField()  # Display group name

    class Meta:
        model = GroupMembership
        fields = ['id', 'user', 'group', 'role', 'joined_at']

class GroupResourceSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()  # Display user string (username)
    group = serializers.StringRelatedField()  # Display group name

    class Meta:
        model = GroupResource
        fields = ['id', 'title', 'description', 'file', 'uploaded_by', 'group', 'upload_date']

class GroupDiscussionSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()  # Display user string (username)
    group = serializers.StringRelatedField()  # Display group name
    comments_count = serializers.IntegerField(source='discussioncomment_set.count', read_only=True)  # Count comments in discussion

    class Meta:
        model = GroupDiscussion
        fields = ['id', 'title', 'content', 'group', 'created_by', 'created_at', 'is_pinned', 'comments_count']

class DiscussionCommentSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()  # Display user string (username)
    discussion = serializers.StringRelatedField()  # Display discussion title

    class Meta:
        model = DiscussionComment
        fields = ['id', 'discussion', 'content', 'created_by', 'created_at']
