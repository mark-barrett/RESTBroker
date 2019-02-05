import json
import random
import string

from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from core.forms import *
from core.models import *

from sshtunnel import SSHTunnelForwarder

import MySQLdb as db

from core.tasks import build_database


class Home(View):

    def get(self, request):
        return render(request, 'core/home.html')


    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        # Try log the user in
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Hey ' + user.first_name + ', welcome back!')
            return redirect('/dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('/')


class SignUp(View):

    def get(self, request):

        return render(request, 'core/sign-up.html')

    def post(self, request):

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Check if the user exists by email or username
        try:
            user = User.objects.get(username=username)

            messages.error(request, 'User with that username already exists')
            return redirect('/sign-up')
        except:

            try:
                user = User.objects.get(email=email)

                messages.error(request, 'User with that email already exists')
                return redirect('/sign-up')
            except:
                # All okay, let's register the user.
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                                email=email)

                user.set_password(password)

                user.save()

                user = authenticate(username=username, password=password)

                if user is not None:
                    messages.success(request, 'User sign up successful')
                    login(request, user)
                    return redirect('/dashboard')
                else:
                    messages.error(request, 'Error signing you up')
                    return redirect('/sign-up')


class Logout(View):

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, "Logged out. Thanks for stopping by!")
            return redirect('/')


class Dashboard(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):

        context = {
            'projects': Project.objects.all().filter(user=request.user)
        }

        return render(request, 'core/dashboard.html', context)


class CreateProject(LoginRequiredMixin, View):

    def get(self, request):
        context = {
            'form': ProjectForm(request=request, edit=False),
            'projects': Project.objects.all().filter(user=request.user),
            'action': 'Create'
        }

        return render(request, 'core/create-edit-project.html', context)

    def post(self, request):
        form = ProjectForm(request.POST, request=request)

        if form.is_valid():
            project = form.save(commit=False)

            project.user = request.user

            if 'type' not in request.POST:
                context = {
                    'form': form,
                    'projects': Project.objects.all().filter(user=request.user)
                }

                messages.error(request, 'Please choose a project type.')

                return render(request, 'core/create-edit-project.html', context)
            else:
                project.type = request.POST['type']

            project.save()

            if project.type == 'private':
                # Now that a project has been created lets generate an API key for it.
                api_key_not_found = True

                key = ''

                while api_key_not_found:
                    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))

                    key = 'rb_key_'+key

                    try:
                        api_key = APIKey.objects.get(key=key)
                    except:
                        api_key_not_found = False

                api_key = APIKey(
                    key=key,
                    user=request.user,
                    project=project
                )

                api_key.save()

                messages.success(request, 'Project and API Key created successfully.')
            else:
                messages.success(request, 'Project created successfully.')

            return redirect('/project/'+str(project.id))
        else:
            context = {
                'form': form,
                'projects': Project.objects.all().filter(user=request.user)
            }
            return render(request, 'core/create-edit-project.html', context)


class ViewProject(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, project_id):

        try:
            # Get the project
            project = Project.objects.get(id=project_id)

            # Check to make sure the user viewing this project is the owner of it
            if project.user == request.user:
                context = {
                    'project': project,
                    'projects': Project.objects.all().filter(user=request.user)
                }

                return render(request, 'core/project.html', context)
            else:
                messages.error(request, 'Sorry, we can\'t seem to find what you were looking for.')
                return redirect('/dashboard')
        except:
            messages.error(request, 'Project does not exist.')
            return redirect('/dashboard')


class EditProject(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, project_id):

        try:
            # Get the project
            project = Project.objects.get(id=project_id)

            # Check to make sure the user viewing this project is the owner of it
            if project.user == request.user:

                context = {
                    'form': ProjectForm(instance=project, edit=True),
                    'projects': Project.objects.all().filter(user=request.user),
                    'action': 'Edit',
                    'project': project
                }

                return render(request, 'core/create-edit-project.html', context)
            else:
                messages.error(request, 'Sorry, we can\'t seem to find what you were looking for.')
                return redirect('/dashboard')
        except:
            messages.error(request, 'Project does not exist.')
            return redirect('/dashboard')


    def post(self, request, project_id):

        project = Project.objects.get(id=project_id)

        form = ProjectForm(request.POST, instance=project, request=request, project_id=project_id)

        if form.is_valid():
            project = form.save(commit=False)

            project.user = request.user

            if 'type' not in request.POST:
                context = {
                    'form': form,
                    'projects': Project.objects.all().filter(user=request.user)
                }

                messages.error(request, 'Please choose a project type.')

                return render(request, 'core/create-edit-project.html', context)
            else:
                project.type = request.POST['type']

            project.save()

            messages.success(request, 'Project edited successfully.')
            return redirect('/project/' + str(project.id))
        else:
            context = {
                'form': form,
                'projects': Project.objects.all().filter(user=request.user)
            }
            return render(request, 'core/create-edit-project.html', context)


class DeleteProject(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, project_id):
        # Get the project
        project = Project.objects.get(id=project_id)

        # Check the ownership
        if project.user == request.user:
            # Confirmed that they own the project. Delete and redirect to the dashboard with a message.
            project.delete()

            messages.success(request, 'Successfully deleted project.')
            return redirect('/dashboard')


class BuildDatabase(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, project_id):
        try:
            # Get the project
            project = Project.objects.get(id=project_id)

            # Check to make sure the user viewing this project is the owner of it
            if project.user == request.user:

                context = {
                    'form': DatabaseBuilderForm(),
                    'project_id': project_id,
                    'projects': Project.objects.all().filter(user=request.user)
                }

                return render(request, 'core/build-database.html', context)
            else:
                messages.error(request, 'Sorry, we can\'t seem to find what you were looking for.')
                return redirect('/dashboard')
        except Exception as e:
            print(e)
            messages.error(request, 'Project does not exist.')
            return redirect('/dashboard')


    def post(self, request, project_id):

        try:
            ssh_address = request.POST['ssh_address']
            ssh_user = request.POST['ssh_user']
            ssh_password = request.POST['ssh_password']
            database_name = request.POST['database_name']
            database_user = request.POST['database_user']
            database_password = request.POST['database_password']

            try:
                # Get the project
                project = Project.objects.get(id=project_id)

                # Check to make sure the user viewing this project is the owner of it
                if project.user == request.user:

                    # Now that we have all of the information let us test the SSH Tunnel.
                    # Pass it to Celery to deal with
                    async_result = build_database.delay(project_id=project.id, ssh_address=ssh_address, ssh_user=ssh_user,
                                                        ssh_password=ssh_password, database_name=database_name,
                                                        database_user=database_user,
                                                        database_password=database_password)

                    response = {
                        'message': async_result.get()
                    }

                    print(response)

                    return HttpResponse(json.dumps(response), content_type='application/json')

                else:
                    messages.error(request, 'Sorry, we can\'t seem to find what you were looking for.')
                    return redirect('/dashboard')
            except Exception as e:
                print(e)
                messages.error(request, 'Project does not exist.')
                return redirect('/dashboard')

        except Exception as e:

            response = {
                'message': str(e)
            }
            return HttpResponse(json.dumps(response), content_type='application/json')


class CreateEndpoint(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, project_id):

        context = {
            'form': EndpointForm(request=request),
            'project_id': project_id,
            'projects': Project.objects.all().filter(user=request.user)
        }

        # If its the second step
        if 'endpoint' in request.session:

            database_data = {
                'tables': []
            }

            # Get the database using the project_id
            database = Database.objects.get(project=Project.objects.get(id=project_id))

            # Add the database tables and columns to the context
            tables = DatabaseTable.objects.all().filter(database=database)

            # Loop through all tables
            for table in tables:
                table_obj = {
                    'id': table.id,
                    'name': table.name,
                    'columns': []
                }

                columns = DatabaseColumn.objects.all().filter(table=table)

                # Loop through all columns
                for column in columns:
                    column_obj = {
                        'id': column.id,
                        'name': column.name,
                        'type': column.type
                    }

                    # Append it
                    table_obj['columns'].append(column_obj)

                # Append the table to the database_data
                database_data['tables'].append(table_obj)

            context['database_data'] = json.dumps(database_data)

        return render(request, 'core/create-endpoint.html', context)


    def post(self, request, project_id):
        form = EndpointForm(request.POST, request=request)

        if form.is_valid():
            # Get the values from the form, set it to a session and send back to the same page
            endpoint = {
                'project': project_id,
                'name': form.cleaned_data['name'],
                'description': form.cleaned_data['description'],
                'request': {
                    'type': form.cleaned_data['request_type'],
                    'url': form.cleaned_data['endpoint_url'],
                    'headers': [],
                    'parameters': []
                }
            }

            # Get the headers as lists
            header_keys = request.POST.getlist('header-key')
            header_value = request.POST.getlist('header-value')
            header_description = request.POST.getlist('header-description')

            # Loop through the keys and add the headers to the endpoint object.
            for index, key in enumerate(header_keys):
                header = {
                    'key': key,
                    'value': header_value[index],
                    'description': header_description[index]
                }

                endpoint['request']['headers'].append(header)

            # Get the parameters as lists
            parameter_types = request.POST.getlist('parameter-type')
            parameter_keys = request.POST.getlist('parameter-key')

            # Loop through them and add them to the endpoint
            for index, key in enumerate(parameter_keys):
                parameter = {
                    'type': parameter_types[index],
                    'key': key
                }

                endpoint['request']['parameters'].append(parameter)

            # Set this as a session variable.
            request.session['endpoint'] = endpoint

            # Now that the session is set, redirect back to create an endpoint to create the response
            return redirect('/endpoint/create/'+project_id)


class Account(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request):

        context = {
            'projects': Project.objects.all().filter(user=request.user)
        }

        return render(request, 'core/account.html', context)


class ProjectSettings(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, project_id):

        context = {
            'projects': Project.objects.all().filter(user=request.user),
            'project': Project.objects.get(id=project_id)
        }

        return render(request, 'core/project-settings.html', context)


class APIKeys(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, project_id):

        project = Project.objects.get(id=project_id)

        context = {
            'projects': Project.objects.all().filter(user=request.user),
            'project': project,
            'api_keys': APIKey.objects.all().filter(project=project)
        }

        return render(request, 'core/api-keys.html', context)