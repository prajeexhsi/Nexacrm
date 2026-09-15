from django.contrib import admin
from .models import Lead,Student,Course,FollowUp,Payment,Task,Ticket,MarketingCampaign,Message,Activity,WorkspaceSetting
for model in [Lead,Student,Course,FollowUp,Payment,Task,Ticket,MarketingCampaign,Message,Activity,WorkspaceSetting]: admin.site.register(model)
