from django.db import models

class Client(models.Model):
    client_id = models.AutoField(db_column='ClientID', primary_key=True)  
    client_name = models.CharField(db_column='ClientName', max_length=255, blank=True, null=True)  
    address = models.CharField(max_length=255, blank=True, null=True)  
    xero_id = models.CharField(db_column='XeroID', max_length=255, blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'clients'
    
    def __str__(self):
        return (f"{self.client_name}")

class Employee(models.Model):
    employee_id = models.AutoField(db_column='EmployeeID', primary_key=True)  
    name = models.CharField(max_length=255, blank=True, null=True)  
    phone = models.CharField(max_length=20, blank=True, null=True)  
    email = models.CharField(max_length=255, blank=True, null=True)  
    xero_id = models.CharField(db_column='XeroID', max_length=255, blank=True, null=True)  
    general_labour = models.BooleanField(db_column='GeneralLabour', blank=True, default=False)
    traffic_controller = models.BooleanField(db_column='TrafficController', blank=True, default=False)
    first_aider = models.BooleanField(db_column='FirstAider', blank=True, default=False)
    construction_cleaner = models.BooleanField(db_column='ConstructionCleaner', blank=True, default=False)
    boom_lift = models.BooleanField(db_column='BoomLift', blank=True, default=False)
    telehandler = models.BooleanField(db_column='Telehandler', blank=True, default=False)
    forklift_driver = models.BooleanField(db_column='ForkliftDriver', blank=True, default=False)
    hoister_driver = models.BooleanField(db_column='HoisterDriver', blank=True, default=False)
  

    class Meta:
        managed = True
        db_table = 'employees'
   
    def __str__(self):
        return (f"{self.employee_id} {self.name} {self.phone} ")

class JobRole(models.Model):
    job_role_id = models.AutoField(db_column='JobRoleID', primary_key=True)  
    role_description = models.CharField(db_column='RoleDescription', max_length=255, blank=True, null=True)  
    rate = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)  
    rate_1_5x = models.DecimalField(db_column='Rate1_5x', max_digits=10, decimal_places=2, blank=True, null=True) # Optional
    rate_2x = models.DecimalField(db_column='Rate2x', max_digits=10, decimal_places=2, blank=True, null=True) # Optional
    travel = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # Optional
    pay = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False) # Required
    pay_1_5x = models.DecimalField(db_column='Pay1_5x', max_digits=10, decimal_places=2, blank=True, null=True) # Optional
    pay_2x = models.DecimalField(db_column='Pay2x', max_digits=10, decimal_places=2, blank=True, null=True) # Optional
    job = models.ForeignKey('Job', on_delete=models.CASCADE, db_column='JobID', blank=False, null=False) # Required

    def __str__(self):
        return (f"{self.role_description}")
    class Meta:
        managed = True
        db_table = 'jobroles'
class Job(models.Model):  
    STATE_CHOICES = [
        ('HOTNSW', 'HOT NSW'),
        ('NSW', 'NSW'),
        ('QLD', 'QLD'),
        ('VIC', 'VIC'),
        ('WA', 'WA'),
    ]
    job_id = models.AutoField(db_column='JobID', primary_key=True)  
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='ClientID', blank=True, null=True)  
    po_name = models.CharField(db_column='POName', max_length=255, blank=True, null=True)  
    address = models.CharField(max_length=255, blank=True, null=True)  
    state = models.CharField(max_length=50, choices=STATE_CHOICES, blank=False, null=False)  
    

    def __str__(self):
        return (f"{self.po_name}")
    class Meta:
        managed = True
        db_table = 'jobs'


class Invoice(models.Model):
    
    invoice_id = models.AutoField(db_column='InvoiceID', primary_key=True)  
    job = models.ForeignKey(Job, on_delete=models.CASCADE, db_column='JobID', blank=True, null=True)  
    role_description = models.TextField(db_column='RoleDescription', blank=True, null=True)  
    due_date = models.DateField(db_column='DueDate', blank=True, null=True)  
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  
    worked_hours = models.DecimalField(db_column='WorkedHours', max_digits=10, decimal_places=2, blank=True, null=True)  
    invoice_total = models.DecimalField(db_column='InvoiceTotal', max_digits=10, decimal_places=2, blank=True, null=True)  
    gst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  
    profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'invoices'


class JobAssignment(models.Model):
    job_assignment_id = models.AutoField(db_column='JobAssignmentID', primary_key=True)  
    job = models.ForeignKey(Job, on_delete=models.CASCADE, db_column='JobID',  blank=True)  
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='EmployeeID', blank=True )  
    job_role = models.ForeignKey('JobRole', on_delete=models.CASCADE, db_column='JobRoleID', blank=True )   
    date = models.DateField(blank=True)  
    start_time = models.TimeField(db_column='StartTime', blank=True, null=True)  
    finish_time = models.TimeField(db_column='FinishTime', blank=True, null=True)  
    lunch_hours = models.DecimalField(db_column='LunchHours', max_digits=3, decimal_places=1, blank=True, null=True)  

    class Meta:
        managed = True
        db_table = 'jobassignments'


    def __str__(self):
        return (f"{self.job_assignment_id} {self.job} {self.employee} {self.job_role} {self.date}")






