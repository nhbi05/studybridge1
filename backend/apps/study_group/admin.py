from django.contrib import admin
from .models import StudyGroup,GroupMembership,GroupDiscussion,GroupResource,DiscussionComment
# Register your models here.
admin.site.register(StudyGroup)
admin.site.register(GroupMembership)
admin.site.register(GroupResource)
admin.site.register(GroupDiscussion)
admin.site.register(DiscussionComment)