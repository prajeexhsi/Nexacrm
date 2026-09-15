from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("auth", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Lead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("phone", models.CharField(max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("course", models.CharField(blank=True, max_length=120)),
                ("source", models.CharField(choices=[("Website", "Website"), ("Facebook", "Facebook"), ("Instagram", "Instagram"), ("WhatsApp", "WhatsApp"), ("Walk-in", "Walk-in"), ("Referral", "Referral"), ("Other", "Other")], default="Website", max_length=30)),
                ("status", models.CharField(choices=[("New", "New"), ("Contacted", "Contacted"), ("Interested", "Interested"), ("Follow-up", "Follow-up"), ("Converted", "Converted"), ("Not Interested", "Not Interested")], default="New", max_length=30)),
                ("priority", models.CharField(choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")], default="Medium", max_length=10)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_leads", to="auth.user")),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("phone", models.CharField(max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("course", models.CharField(blank=True, max_length=120)),
                ("admission_date", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("Enquiry", "Enquiry"), ("Active", "Active"), ("Completed", "Completed"), ("Dropped", "Dropped")], default="Enquiry", max_length=20)),
                ("source", models.CharField(blank=True, max_length=30)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assigned_students", to="auth.user")),
            ],
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("duration", models.CharField(blank=True, max_length=80)),
                ("fee", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("batch", models.CharField(blank=True, max_length=100)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="FollowUp",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scheduled_at", models.DateTimeField()),
                ("status", models.CharField(choices=[("Today", "Today"), ("Upcoming", "Upcoming"), ("Overdue", "Overdue"), ("Completed", "Completed")], default="Upcoming", max_length=20)),
                ("note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="followups", to="auth.user")),
                ("lead", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="followups", to="crmapp.lead")),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(max_length=120)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(choices=[("Paid", "Paid"), ("Pending", "Pending"), ("Partial", "Partial"), ("Refunded", "Refunded")], default="Pending", max_length=20)),
                ("method", models.CharField(default="Cash", max_length=40)),
                ("reference", models.CharField(blank=True, max_length=100)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("student", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payments", to="crmapp.student")),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("description", models.TextField(blank=True)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("priority", models.CharField(choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")], default="Medium", max_length=10)),
                ("completed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="tasks", to="auth.user")),
            ],
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("customer_name", models.CharField(max_length=120)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("description", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("Open", "Open"), ("In Progress", "In Progress"), ("Resolved", "Resolved"), ("Closed", "Closed")], default="Open", max_length=20)),
                ("priority", models.CharField(choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High")], default="Medium", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="tickets", to="auth.user")),
            ],
        ),
        migrations.CreateModel(
            name="MarketingCampaign",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("channel", models.CharField(default="Instagram", max_length=50)),
                ("budget", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("leads", models.PositiveIntegerField(default=0)),
                ("conversions", models.PositiveIntegerField(default=0)),
                ("status", models.CharField(choices=[("Draft", "Draft"), ("Running", "Running"), ("Completed", "Completed")], default="Draft", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("template", models.CharField(default="Enquiry Received", max_length=80)),
                ("body", models.TextField()),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
                ("channel", models.CharField(default="WhatsApp", max_length=20)),
                ("lead", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="crmapp.lead")),
                ("sent_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
            ],
        ),
        migrations.CreateModel(
            name="Activity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("lead", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="activities", to="crmapp.lead")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
            ],
        ),
        migrations.CreateModel(
            name="WorkspaceSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("business_type", models.CharField(default="Education / Training Institute", max_length=80)),
                ("business_description", models.TextField(blank=True)),
                ("modules", models.JSONField(blank=True, default=list)),
                ("onboarding_complete", models.BooleanField(default=False)),
                ("plan", models.CharField(default="Starter", max_length=30)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="workspace", to="auth.user")),
            ],
        ),
    ]
