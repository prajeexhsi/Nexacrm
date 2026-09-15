from django.db import models
from django.contrib.auth.models import User

class Lead(models.Model):
    STATUS_CHOICES=[("New","New"),("Contacted","Contacted"),("Interested","Interested"),("Follow-up","Follow-up"),("Converted","Converted"),("Not Interested","Not Interested")]
    SOURCE_CHOICES=[("Website","Website"),("Facebook","Facebook"),("Instagram","Instagram"),("WhatsApp","WhatsApp"),("Walk-in","Walk-in"),("Referral","Referral"),("Other","Other")]
    PRIORITY_CHOICES=[("Low","Low"),("Medium","Medium"),("High","High")]
    name=models.CharField(max_length=120); phone=models.CharField(max_length=30); email=models.EmailField(blank=True)
    course=models.CharField(max_length=120,blank=True); source=models.CharField(max_length=30,choices=SOURCE_CHOICES,default="Website")
    status=models.CharField(max_length=30,choices=STATUS_CHOICES,default="New"); priority=models.CharField(max_length=10,choices=PRIORITY_CHOICES,default="Medium")
    assigned_to=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name="assigned_leads")
    notes=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    def __str__(self): return self.name

class Student(models.Model):
    STATUS_CHOICES=[("Enquiry","Enquiry"),("Active","Active"),("Completed","Completed"),("Dropped","Dropped")]
    name=models.CharField(max_length=120); phone=models.CharField(max_length=30); email=models.EmailField(blank=True)
    course=models.CharField(max_length=120,blank=True); admission_date=models.DateField(null=True,blank=True); status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="Enquiry")
    source=models.CharField(max_length=30,blank=True); assigned_to=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name="assigned_students")
    notes=models.TextField(blank=True); created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Course(models.Model):
    name=models.CharField(max_length=150); duration=models.CharField(max_length=80,blank=True); fee=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    batch=models.CharField(max_length=100,blank=True); start_date=models.DateField(null=True,blank=True); active=models.BooleanField(default=True)
    def __str__(self): return self.name

class FollowUp(models.Model):
    STATUS_CHOICES=[("Today","Today"),("Upcoming","Upcoming"),("Overdue","Overdue"),("Completed","Completed")]
    lead=models.ForeignKey(Lead,on_delete=models.CASCADE,related_name="followups"); scheduled_at=models.DateTimeField(); status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="Upcoming")
    note=models.TextField(blank=True); assigned_to=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name="followups"); created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.lead.name} - {self.scheduled_at:%d %b %Y %I:%M %p}"

class Payment(models.Model):
    STATUS_CHOICES=[("Paid","Paid"),("Pending","Pending"),("Partial","Partial"),("Refunded","Refunded")]
    student=models.ForeignKey(Student,null=True,blank=True,on_delete=models.SET_NULL,related_name="payments"); customer_name=models.CharField(max_length=120)
    amount=models.DecimalField(max_digits=12,decimal_places=2); status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="Pending"); method=models.CharField(max_length=40,default="Cash")
    reference=models.CharField(max_length=100,blank=True); paid_at=models.DateTimeField(null=True,blank=True); created_at=models.DateTimeField(auto_now_add=True)

class Task(models.Model):
    PRIORITY_CHOICES=[("Low","Low"),("Medium","Medium"),("High","High")]
    title=models.CharField(max_length=180); description=models.TextField(blank=True); due_date=models.DateField(null=True,blank=True); priority=models.CharField(max_length=10,choices=PRIORITY_CHOICES,default="Medium")
    assigned_to=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name="tasks"); completed=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)

class Ticket(models.Model):
    STATUS_CHOICES=[("Open","Open"),("In Progress","In Progress"),("Resolved","Resolved"),("Closed","Closed")]
    PRIORITY_CHOICES=[("Low","Low"),("Medium","Medium"),("High","High")]
    title=models.CharField(max_length=180); customer_name=models.CharField(max_length=120); email=models.EmailField(blank=True); description=models.TextField(blank=True)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="Open"); priority=models.CharField(max_length=10,choices=PRIORITY_CHOICES,default="Medium"); assigned_to=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name="tickets"); created_at=models.DateTimeField(auto_now_add=True)

class MarketingCampaign(models.Model):
    STATUS_CHOICES=[("Draft","Draft"),("Running","Running"),("Completed","Completed")]
    name=models.CharField(max_length=150); channel=models.CharField(max_length=50,default="Instagram"); budget=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    leads=models.PositiveIntegerField(default=0); conversions=models.PositiveIntegerField(default=0); status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="Draft"); created_at=models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    lead=models.ForeignKey(Lead,on_delete=models.CASCADE,related_name="messages"); template=models.CharField(max_length=80,default="Enquiry Received"); body=models.TextField(); sent_at=models.DateTimeField(auto_now_add=True); sent_by=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL); channel=models.CharField(max_length=20,default="WhatsApp")

class Activity(models.Model):
    lead=models.ForeignKey(Lead,null=True,blank=True,on_delete=models.CASCADE,related_name="activities"); user=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL); action=models.CharField(max_length=255); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-created_at"]

class WorkspaceSetting(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="workspace")
    business_type=models.CharField(max_length=80,default="Education / Training Institute"); business_description=models.TextField(blank=True)
    modules=models.JSONField(default=list,blank=True); onboarding_complete=models.BooleanField(default=False); plan=models.CharField(max_length=30,default="Starter")
    def __str__(self): return f"{self.user.username} workspace"
