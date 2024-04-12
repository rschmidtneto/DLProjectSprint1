from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.views import View
from collections import defaultdict
from datetime import datetime, timedelta
from .models import Client, Employee, Invoice, JobAssignment, JobRole, Job
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordChangeForm



def home(request):

    """
    Handles user login. POST to authenticate, GET to serve login page.

    """    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        #authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in.")
            return redirect('roaster')
        else:
            messages.error(request, "There was an error while logging in.")
            return render(request, 'login.html', {})

    else:
        return render(request, 'login.html', { })



def logout_user(request):
    """
    Logs out the user and redirects to home.

    """
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

class RoasterView(View):
    """
    Displays roaster for jobs assigned within a week, filtered by state.
    Handles both AJAX and normal requests.

    """

    def get(self, request, *arg, **kwargs):
        week_start_str = request.GET.get('week_start')
        selected_state = request.GET.get('state')  

        if week_start_str:
            start_week = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        else:
            today = datetime.now().date()
            start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)

        # Generate dates for the entire week for display purposes
        week_dates = [start_week + timedelta(days=x) for x in range(7)]

        # Fetch jobs based on the selected state
        if selected_state:
            jobs = Job.objects.filter(state=selected_state)
        else:
            jobs  = Job.objects.filter(state='NSW')

        # Fetch assignments within the specified week
        assignments = JobAssignment.objects.filter(date__range=[start_week, end_week]).select_related('job', 'employee')

        # Initialize job_assignment dictionary with all jobs, ensuring each job appears regardless of having assignments
        job_assignments = {job: [] for job in jobs}

        
        for assignment in assignments:
            if assignment.job in job_assignments:  # This check ensures that only jobs fetched above are considered
                job_assignments[assignment.job].append(assignment)
            

        context = {
            'job_assignments': job_assignments,
            'week_dates': week_dates,
            'selected_state': selected_state,
        }

        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('roaster_table.html', context, request=request)
            return HttpResponse(html)

        return render(request, 'roaster.html', context)
    

def viewBooking(request, pk):
    """
    View or edit an existing booking.
    
    """
    schedule = get_object_or_404(JobAssignment, pk=pk)
    date_obj = schedule.date
    jobId_obj= schedule.job_id
    jobRoles = JobRole.objects.filter(job_id=schedule.job_id)

    if request.user.is_authenticated: 
        html = render_to_string('edit_booking.html', {'jobId_obj' : jobId_obj, 'date_obj':date_obj, 'jobRoles':jobRoles, 'schedule':schedule }, request=request)
        return HttpResponse(html)
        
    else:
        messages.success(request, "Please log in.")
        return redirect('home')
    
    

def addBooking(request, jobId, date):
    """
    GET to add a new booking.
    
    """
    date_obj = datetime.strptime(date, '%Y-%m-%d').date()
    jobId_obj= Job.objects.get(job_id=jobId)
    jobRoles = JobRole.objects.filter(job_id=jobId) 
    if request.user.is_authenticated: 
        html = render_to_string('add_booking.html', {'jobId_obj' : jobId_obj, 'date_obj':date_obj, 'jobRoles':jobRoles }, request=request)
        return HttpResponse(html)
        
    else:
        messages.success(request, "Please log in.")
        return redirect('home')
    
def createBooking(request):
    """
    POST to create a new booking.
    
    """
    if request.user.is_authenticated: 
        if request.method == "POST":
            jobId = request.POST.get('jobid')
            employeeId = request.POST.get('employeeid')
            jobRoleId = request.POST.get('jobRoleid')
            dateStr = request.POST.get('date')
            date = datetime.strptime(dateStr, '%Y-%m-%d').date()
            
            # Fetch model instances
            try:
                job = Job.objects.get(pk=jobId)
                employee = Employee.objects.get(pk=employeeId)
                jobRole = JobRole.objects.get(pk=jobRoleId)
                
                JobAssignment.objects.create(job=job, employee=employee, job_role=jobRole, date=date)
                return HttpResponse('Success')
            except (Job.DoesNotExist, Employee.DoesNotExist, JobRole.DoesNotExist) as e:
                return HttpResponse(f'Error: {e}', status=400)
        else:
            return HttpResponse('Request must be POST', status=400)
    else:
        return HttpResponse('Unauthorized', status=401)



    

def editBooking(request, pk):
    """
    POST to edit a booking.
    
    """
    
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)
    
    if request.method != "POST":
        return HttpResponse('Request must be POST', status=400)

    # Fetch the JobAssignment instance by pk
    job_assignment = get_object_or_404(JobAssignment, pk=pk)
    
    # Update fields from POST data if available
    employee_id = request.POST.get('employeeid')
    job_role_id = request.POST.get('jobRoleid')

    try:
        if employee_id:
            employee = Employee.objects.get(pk=employee_id)
            job_assignment.employee = employee  # Update the employee

        if job_role_id:
            job_role = JobRole.objects.get(pk=job_role_id)
            job_assignment.job_role = job_role  # Update the job role

        # Save the updated job_assignment
        job_assignment.save()
        return HttpResponse('Success')

    except (Employee.DoesNotExist, JobRole.DoesNotExist) as e:
        return HttpResponse(f'Error: {e}', status=400)
    
    

def deleteBooking(request, pk):
    """
    POST to delete a booking.
    
    """
    if request.user.is_authenticated:    
        if request.method == "POST":
            delete_it = get_object_or_404(JobAssignment, job_assignment_id=pk)
            delete_it.delete()
            messages.success(request, "Booking deleted.")
            return HttpResponse('Success')
        else:
            messages.error(request, "Ops there was an error deleting this booking.")
            return HttpResponse("Failure", status=400)
    else:
        messages.success(request, "Please log in.")
        return redirect('home')

def getEmployees(request):
    """
    GET to search employees on the database and return succeful response to ajax.
    
    """
    if request.user.is_authenticated:
        context = {}
        url_parameter = request.GET.get("q")

        if url_parameter:
            employees = Employee.objects.filter(name__icontains=url_parameter)
            context["employees"] = employees
            return render(request, "replace_employee.html", context=context)
        else:
            employees = Employee.objects.none()
            context["employees"] = employees

        return render(request, "get_employee.html", context=context)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('replace_employee.html', context, request=request)
            return HttpResponse(html)
    
    else:
        messages.success(request, "Please log in.")
        return redirect('home')
    
def getJobRoles(request, pk):
    """
    GET to search job roles on the database and return it to the dropdown menus.
    
    """
    if request.user.is_authenticated:
        jobRoles = JobRole.objects.filter(job_id=pk)  
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            html = render_to_string('jobrole_replace.html', {'jobRoles': jobRoles}, request=request)
            print("response was sent to ajax")
            return HttpResponse(html)
        else:
            jobRoles = JobRole.objects.filter(job_role_id=pk)
            print(jobRoles)
            return HttpResponse("Not an ajax request")
            
    else:
        messages.success(request, "Please log in.")
        return redirect('home')
    

def change_password(request):
    """
    POST form to change the password
    
    """
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  
                messages.success(request, 'Your password was successfully updated!')
                return redirect('roaster')
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            form = PasswordChangeForm(request.user)
        return render(request, 'change_password.html', {
            'form': form })
    else:
        return redirect('home')
        

