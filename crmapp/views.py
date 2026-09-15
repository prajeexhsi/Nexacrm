import csv, json
from io import BytesIO
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages as django_messages
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from .forms import *
from .models import *

def log_activity(request, action, lead=None): Activity.objects.create(user=request.user, lead=lead, action=action)

def landing(request):
    if request.user.is_authenticated: return redirect("dashboard")
    return render(request,"landing.html")

def login_view(request):
    if request.user.is_authenticated: return redirect("dashboard")
    if request.method=="POST":
        ident=request.POST.get("username","").strip(); password=request.POST.get("password",""); username=ident
        if "@" in ident:
            u=User.objects.filter(email__iexact=ident).first(); username=u.username if u else ident
        user=authenticate(request,username=username,password=password)
        if user:
            login(request,user)
            ws,_=WorkspaceSetting.objects.get_or_create(user=user,defaults={"modules":["Leads","Students","Courses","Follow-ups","Payments","Reports"]})
            return redirect("dashboard" if ws.onboarding_complete else "onboarding_step", step=1)
        django_messages.error(request,"Invalid username/email or password.")
    return render(request,"registration/login.html")

def register_view(request):
    if request.user.is_authenticated: return redirect("dashboard")
    if request.method=="POST":
        full=request.POST.get("full_name","").strip(); username=request.POST.get("username","").strip(); email=request.POST.get("email","").strip(); pw=request.POST.get("password",""); cpw=request.POST.get("confirm_password","")
        if not all([full,username,email,pw]): django_messages.error(request,"Please complete all required fields.")
        elif pw!=cpw: django_messages.error(request,"Passwords do not match.")
        elif User.objects.filter(username__iexact=username).exists(): django_messages.error(request,"Username already exists.")
        elif User.objects.filter(email__iexact=email).exists(): django_messages.error(request,"Email is already registered.")
        else:
            u=User.objects.create_user(username=username,email=email,password=pw,first_name=full); WorkspaceSetting.objects.create(user=u,modules=["Leads","Students","Courses","Follow-ups","Payments","Reports"]); django_messages.success(request,"Account created. Please login."); return redirect("login")
    return render(request,"register.html")

def logout_view(request): logout(request); return redirect("login")

@login_required
def onboarding(request,step=1):
    ws,created=WorkspaceSetting.objects.get_or_create(user=request.user,defaults={"modules":["Leads","Students","Courses","Follow-ups","Payments","Reports"]})
    if request.method=="POST":
        if step==1: ws.business_type=request.POST.get("business_type",ws.business_type); ws.save(); return redirect("onboarding_step",step=2)
        if step==2: ws.modules=request.POST.getlist("modules"); ws.save(); return redirect("onboarding_step",step=3)
        ws.business_description=request.POST.get("business_description",""); ws.onboarding_complete=True; ws.save(); return redirect("onboarding_ready")
    business=["Education / Training Institute","Small Business","Sales Team","Marketing Agency","Healthcare / Clinic","Real Estate","IT / Software Company","Shop / E-commerce","Freelancer","Custom / Other"]
    modules=["Leads","Students","Courses","Follow-ups","Payments","Tasks","Marketing","Support"]
    return render(request,"onboarding.html",{"step":step,"ws":ws,"business_types":business,"modules":modules})
@login_required
def onboarding_ready(request):
    ws,_=WorkspaceSetting.objects.get_or_create(user=request.user,defaults={"modules":["Leads","Students","Courses","Follow-ups","Payments","Reports"]})
    return render(request,"onboarding_ready.html",{"ws":ws})

@login_required
def dashboard(request):
    leads=Lead.objects.all(); today=timezone.localdate(); payments=Payment.objects.all()
    status_counts=list(leads.values("status").annotate(count=Count("id")))
    context={"total_leads":leads.count(),"new_leads":leads.filter(status="New").count(),"converted":leads.filter(status="Converted").count(),"pending":FollowUp.objects.filter(status__in=["Today","Overdue"]).count(),"students":Student.objects.count(),"courses":Course.objects.filter(active=True).count(),"revenue":payments.filter(status="Paid").aggregate(v=Sum("amount"))["v"] or 0,"status_counts":status_counts,"today_followups":FollowUp.objects.filter(scheduled_at__date=today).select_related("lead")[:8],"recent_leads":leads.order_by("-created_at")[:8],"tasks":Task.objects.filter(completed=False).order_by("due_date")[:6]}
    return render(request,"crm/dashboard.html",context)

@login_required
def leads(request):
    qs=Lead.objects.select_related("assigned_to").order_by("-created_at"); status=request.GET.get("status"); q=request.GET.get("q","")
    if status: qs=qs.filter(status=status)
    if q: qs=qs.filter(name__icontains=q)|qs.filter(phone__icontains=q)|qs.filter(email__icontains=q)|qs.filter(course__icontains=q)
    return render(request,"crm/leads.html",{"leads":qs.distinct(),"active_status":status,"q":q})
@login_required
def lead_add(request):
    form=LeadForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): lead=form.save(); log_activity(request,f"Created lead {lead.name}",lead); django_messages.success(request,"Lead created."); return redirect("leads")
    return render(request,"crm/lead_form.html",{"form":form,"title":"Add Lead"})
@login_required
def lead_edit(request,pk):
    lead=get_object_or_404(Lead,pk=pk); form=LeadForm(request.POST or None,instance=lead)
    if request.method=="POST" and form.is_valid(): lead=form.save(); log_activity(request,f"Updated lead {lead.name}",lead); django_messages.success(request,"Lead updated."); return redirect("customer_detail",pk=lead.pk)
    return render(request,"crm/lead_form.html",{"form":form,"title":"Edit Lead"})
@login_required
def lead_delete(request,pk):
    lead=get_object_or_404(Lead,pk=pk)
    if request.method=="POST": lead.delete(); django_messages.success(request,"Lead deleted.")
    return redirect("leads")
@login_required
def customers(request): return render(request,"crm/customers.html",{"customers":Lead.objects.filter(status="Converted").order_by("-updated_at")})
@login_required
def customer_detail(request,pk):
    lead=get_object_or_404(Lead,pk=pk); return render(request,"crm/customer_detail.html",{"lead":lead,"timeline":lead.activities.select_related("user"),"followups":lead.followups.order_by("-scheduled_at"),"messages":lead.messages.order_by("-sent_at")})
@login_required
def followups(request):
    f=request.GET.get("filter","Today"); qs=FollowUp.objects.select_related("lead","assigned_to").order_by("scheduled_at"); now=timezone.now()
    if f=="Today": qs=qs.filter(scheduled_at__date=timezone.localdate(),status__in=["Today","Upcoming"])
    elif f=="Overdue": qs=qs.filter(scheduled_at__lt=now).exclude(status="Completed")
    elif f=="Completed": qs=qs.filter(status="Completed")
    elif f=="Upcoming": qs=qs.filter(scheduled_at__gt=now,status="Upcoming")
    return render(request,"crm/followups.html",{"followups":qs,"filter_name":f})
@login_required
def followup_add(request):
    form=FollowUpForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): f=form.save(); log_activity(request,f"Scheduled follow-up for {f.lead.name}",f.lead); django_messages.success(request,"Follow-up scheduled."); return redirect("followups")
    return render(request,"crm/followup_form.html",{"form":form})
@login_required
def followup_complete(request,pk):
    f=get_object_or_404(FollowUp,pk=pk); f.status="Completed"; f.save(); log_activity(request,f"Completed follow-up for {f.lead.name}",f.lead); return redirect(request.META.get("HTTP_REFERER","followups"))
@login_required
def messages(request): return render(request,"crm/messages.html",{"messages":Message.objects.select_related("lead","sent_by").order_by("-sent_at")})
@login_required
def message_send(request):
    form=MessageForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): m=Message.objects.create(lead=form.cleaned_data["lead"],template=form.cleaned_data["template"],body=form.cleaned_data["body"],sent_by=request.user); log_activity(request,f"Prepared WhatsApp message: {m.template}",m.lead); django_messages.success(request,"Message logged."); return redirect("messages")
    return render(request,"crm/message_form.html",{"form":form})

@login_required
def module_list(request,module):
    configs={
      "students":(Student,"Students","student_add","student_edit","student_delete",["name","phone","email","course","status"]),
      "courses":(Course,"Courses","course_add","course_edit","course_delete",["name","duration","fee","batch","active"]),
      "payments":(Payment,"Payments","payment_add","payment_edit","payment_delete",["customer_name","amount","status","method","reference"]),
      "tasks":(Task,"Tasks","task_add","task_edit","task_delete",["title","due_date","priority","assigned_to","completed"]),
      "support":(Ticket,"Support Tickets","ticket_add","ticket_edit","ticket_delete",["title","customer_name","status","priority","assigned_to"]),
      "marketing":(MarketingCampaign,"Marketing","campaign_add","campaign_edit","campaign_delete",["name","channel","budget","leads","conversions","status"]),
    }
    model,title,add,edit,delete,fields=configs[module]; return render(request,"crm/module_list.html",{"objects":model.objects.all().order_by("-id"),"title":title,"add_url":add,"edit_url":edit,"delete_url":delete,"fields":fields,"module":module})

def generic_crud(request,model,form_class,template,title,pk=None,delete=False):
    obj=get_object_or_404(model,pk=pk) if pk else None
    if delete:
        if request.method=="POST": obj.delete(); django_messages.success(request,f"{title} deleted.")
        return redirect({"Student":"students","Course":"courses","Payment":"payments","Task":"tasks","Ticket":"support","Campaign":"marketing"}[title])
    form=form_class(request.POST or None,instance=obj)
    if request.method=="POST" and form.is_valid(): form.save(); django_messages.success(request,f"{title} saved."); return redirect({"Student":"students","Course":"courses","Payment":"payments","Task":"tasks","Ticket":"support","Campaign":"marketing"}[title])
    return render(request,"crm/generic_form.html",{"form":form,"title":("Edit " if obj else "Add ")+title})
@login_required
def student_add(request): return generic_crud(request,Student,StudentForm,"crm/generic_form.html","Student")
@login_required
def student_edit(request,pk): return generic_crud(request,Student,StudentForm,"crm/generic_form.html","Student",pk)
@login_required
def student_delete(request,pk): return generic_crud(request,Student,StudentForm,"crm/generic_form.html","Student",pk,True)
@login_required
def course_add(request): return generic_crud(request,Course,CourseForm,"crm/generic_form.html","Course")
@login_required
def course_edit(request,pk): return generic_crud(request,Course,CourseForm,"crm/generic_form.html","Course",pk)
@login_required
def course_delete(request,pk): return generic_crud(request,Course,CourseForm,"crm/generic_form.html","Course",pk,True)
@login_required
def payment_add(request): return generic_crud(request,Payment,PaymentForm,"crm/generic_form.html","Payment")
@login_required
def payment_edit(request,pk): return generic_crud(request,Payment,PaymentForm,"crm/generic_form.html","Payment",pk)
@login_required
def payment_delete(request,pk): return generic_crud(request,Payment,PaymentForm,"crm/generic_form.html","Payment",pk,True)
@login_required
def task_add(request): return generic_crud(request,Task,TaskForm,"crm/generic_form.html","Task")
@login_required
def task_edit(request,pk): return generic_crud(request,Task,TaskForm,"crm/generic_form.html","Task",pk)
@login_required
def task_delete(request,pk): return generic_crud(request,Task,TaskForm,"crm/generic_form.html","Task",pk,True)
@login_required
def ticket_add(request): return generic_crud(request,Ticket,TicketForm,"crm/generic_form.html","Ticket")
@login_required
def ticket_edit(request,pk): return generic_crud(request,Ticket,TicketForm,"crm/generic_form.html","Ticket",pk)
@login_required
def ticket_delete(request,pk): return generic_crud(request,Ticket,TicketForm,"crm/generic_form.html","Ticket",pk,True)
@login_required
def campaign_add(request): return generic_crud(request,MarketingCampaign,CampaignForm,"crm/generic_form.html","Campaign")
@login_required
def campaign_edit(request,pk): return generic_crud(request,MarketingCampaign,CampaignForm,"crm/generic_form.html","Campaign",pk)
@login_required
def campaign_delete(request,pk): return generic_crud(request,MarketingCampaign,CampaignForm,"crm/generic_form.html","Campaign",pk,True)

@login_required
def toggle_task(request,pk):
    t=get_object_or_404(Task,pk=pk); t.completed=not t.completed; t.save(); return redirect(request.META.get("HTTP_REFERER","tasks"))
@login_required
def reports(request):
    leads=Lead.objects.all(); total=leads.count(); converted=leads.filter(status="Converted").count()
    return render(request,"crm/reports.html",{"total":total,"converted":converted,"conversion_rate":round(converted/total*100,1) if total else 0,"status_counts":list(leads.values("status").annotate(count=Count("id"))),"staff":list(User.objects.annotate(lead_count=Count("assigned_leads")).values("username","lead_count")),"revenue":Payment.objects.filter(status="Paid").aggregate(v=Sum("amount"))["v"] or 0})
@login_required
def users(request): return render(request,"crm/users.html",{"users":User.objects.all().order_by("username")})
@login_required
def user_add(request):
    if not request.user.is_staff:return redirect("users")
    form=UserCreateForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): u=form.save(commit=False); u.set_password(form.cleaned_data["password"]); u.save(); django_messages.success(request,"User created."); return redirect("users")
    return render(request,"crm/user_form.html",{"form":form})
@login_required
def settings_page(request):
    ws,_=WorkspaceSetting.objects.get_or_create(user=request.user)
    if request.method=="POST": ws.business_type=request.POST.get("business_type",ws.business_type); ws.business_description=request.POST.get("business_description",""); ws.modules=request.POST.getlist("modules"); ws.plan=request.POST.get("plan",ws.plan); ws.save(); django_messages.success(request,"Workspace settings saved."); return redirect("settings")
    return render(request,"crm/settings.html",{"ws":ws,"business_types":["Education / Training Institute","Small Business","Sales Team","Marketing Agency","Healthcare / Clinic","Real Estate","IT / Software Company","Shop / E-commerce","Freelancer","Custom / Other"],"modules":["Leads","Students","Courses","Follow-ups","Payments","Tasks","Marketing","Support","Reports"]})
@login_required
def pricing(request): return render(request,"pricing.html")
@login_required
def role_dashboard(request): return render(request,"crm/role_dashboard.html",{"role":"Admin" if request.user.is_staff else "Employee","leads":Lead.objects.count(),"followups":FollowUp.objects.filter(status__in=["Today","Overdue"]).count(),"tasks":Task.objects.filter(completed=False).count(),"revenue":Payment.objects.filter(status="Paid").aggregate(v=Sum("amount"))["v"] or 0})

@login_required
def export_leads_csv(request):
    response=HttpResponse(content_type="text/csv"); response["Content-Disposition"]='attachment; filename="nexacrm_leads.csv"'; w=csv.writer(response); w.writerow(["Name","Phone","Email","Course","Source","Status","Priority","Assigned","Created"])
    for l in Lead.objects.select_related("assigned_to"): w.writerow([l.name,l.phone,l.email,l.course,l.source,l.status,l.priority,l.assigned_to.username if l.assigned_to else "",l.created_at])
    return response

@login_required
def export_leads_xlsx(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"
    headers = ["Name", "Phone", "Email", "Course", "Source", "Status", "Priority", "Assigned", "Created"]
    ws.append(headers)
    for lead in Lead.objects.select_related("assigned_to"):
        ws.append([
            lead.name,
            lead.phone,
            lead.email,
            lead.course,
            lead.source,
            lead.status,
            lead.priority,
            lead.assigned_to.username if lead.assigned_to else "",
            lead.created_at.strftime("%Y-%m-%d %H:%M:%S") if lead.created_at else "",
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="nexacrm_leads.xlsx"'
    return response

@login_required
def export_leads_pdf(request):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), title="NexaCRM Leads")
    data = [["Name", "Phone", "Email", "Course", "Source", "Status", "Priority", "Assigned", "Created"]]
    for lead in Lead.objects.select_related("assigned_to"):
        data.append([
            lead.name,
            lead.phone,
            lead.email,
            lead.course,
            lead.source,
            lead.status,
            lead.priority,
            lead.assigned_to.username if lead.assigned_to else "",
            lead.created_at.strftime("%Y-%m-%d %H:%M:%S") if lead.created_at else "",
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]))
    doc.build([table])
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="nexacrm_leads.pdf"'
    return response

@login_required
def api_notifications(request):
    items=[{"type":"followup","text":f"Follow-up: {x.lead.name} at {x.scheduled_at:%I:%M %p}"} for x in FollowUp.objects.filter(scheduled_at__date=timezone.localdate()).select_related("lead")[:10]]; return JsonResponse({"count":len(items),"items":items})
