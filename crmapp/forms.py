from django import forms
from django.contrib.auth.models import User
from .models import Lead, FollowUp, Student, Course, Payment, Task, Ticket, MarketingCampaign

class StyledModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for f in self.fields.values(): f.widget.attrs.setdefault("class","input")

class LeadForm(StyledModelForm):
    class Meta: model=Lead; fields=["name","phone","email","course","source","status","priority","assigned_to","notes"]
    widgets={"notes":forms.Textarea(attrs={"rows":4})}
class FollowUpForm(StyledModelForm):
    scheduled_at=forms.DateTimeField(input_formats=["%Y-%m-%dT%H:%M"],widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M",attrs={"type":"datetime-local","class":"input"}))
    class Meta: model=FollowUp; fields=["lead","scheduled_at","status","assigned_to","note"]; widgets={"note":forms.Textarea(attrs={"rows":3})}
class MessageForm(forms.Form):
    lead=forms.ModelChoiceField(queryset=Lead.objects.all(),widget=forms.Select(attrs={"class":"input"})); template=forms.ChoiceField(choices=[(x,x) for x in ["Enquiry Received","Course Details","Fee Details","Follow-up Reminder","Admission Confirmation","Thank You"]],widget=forms.Select(attrs={"class":"input"})); body=forms.CharField(widget=forms.Textarea(attrs={"rows":6,"class":"input"}))
class UserCreateForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"input"}))
    class Meta: model=User; fields=["username","first_name","last_name","email","password","is_staff","is_active"]
class StudentForm(StyledModelForm):
    class Meta: model=Student; fields=["name","phone","email","course","admission_date","status","source","assigned_to","notes"]; widgets={"admission_date":forms.DateInput(attrs={"type":"date"}),"notes":forms.Textarea(attrs={"rows":4})}
class CourseForm(StyledModelForm):
    class Meta: model=Course; fields=["name","duration","fee","batch","start_date","active"]; widgets={"start_date":forms.DateInput(attrs={"type":"date"})}
class PaymentForm(StyledModelForm):
    class Meta: model=Payment; fields=["student","customer_name","amount","status","method","reference","paid_at"]; widgets={"paid_at":forms.DateTimeInput(attrs={"type":"datetime-local"})}
class TaskForm(StyledModelForm):
    class Meta: model=Task; fields=["title","description","due_date","priority","assigned_to"]; widgets={"due_date":forms.DateInput(attrs={"type":"date"}),"description":forms.Textarea(attrs={"rows":4})}
class TicketForm(StyledModelForm):
    class Meta: model=Ticket; fields=["title","customer_name","email","description","status","priority","assigned_to"]; widgets={"description":forms.Textarea(attrs={"rows":5})}
class CampaignForm(StyledModelForm):
    class Meta: model=MarketingCampaign; fields=["name","channel","budget","leads","conversions","status"]
