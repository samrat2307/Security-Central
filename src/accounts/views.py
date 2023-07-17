import requests
from datetime import datetime
from accounts.models import Profile
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
import json
import io
from django.core.serializers.json import DjangoJSONEncoder
from .models import *
from .serializers import *
from django.core import serializers
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django_email_verification import send_email
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render
from django.contrib.auth import logout
from datetime import datetime
from django.middleware import csrf
import csv
from io import StringIO
import psycopg2
import pandas as pd
import configparser
from sqlalchemy import create_engine
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.urls import reverse
# url = "postgresql://postgres:samrat123@localhost:5432/SecurityCentralDB"
# conn_string = (url)


config = configparser.ConfigParser()
config.read_file(open(r'static/config.ini'))
DSN = config.get('DB', 'host')
DB = config.get('DB', 'database')
UID = config.get('DB', 'user')
PWD = config.get('DB', 'password')
PORT = config.get('DB', 'port')
url = "postgresql://"+UID + ":"+PWD+"@"+DSN+":"+PORT+"/"+DB
conn_string = (url)

db = create_engine(url)
conn = db.connect()
conn = psycopg2.connect(url)
cur = conn.cursor()


@csrf_exempt
def sendcsv(request):
    if request.method == 'GET':

        with open('static/components_2023-01-05_115543.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            data = [row for row in csv_reader]

        # Construct the response data
        response_data = {
            'scandatetime': '2023-23-04',
            'solutionname': 'SP',
            'projectname': 'ABC',
            'releasename': '2023.1',
            'reportfile': 'data.csv',
            'data': data
        }

        # Make a POST request to the getcsv view with query parameters
        # url = 'http://localhost:8000/getcsv'
        # query_params = {
        #     'scandatetime': response_data['scandatetime'],
        #     'solutionname': response_data['solutionname'],
        #     'projectname': response_data['projectname'],
        #     'releasename': response_data['release']
        # }
        # headers = {'Content-Type': 'application/json'}
        # response = requests.post(url, params=query_params, data=json.dumps(
        #     response_data['data']), headers=headers)

        # Return the response as JSON
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def storescan(request):
    # my_param = request.GET.get('Name', None)
    scandatetime = request.GET.get('scandatetime')
    solutionname = request.GET.get('solutionname')
    projectname = request.GET.get('projectname')
    releasename = request.GET.get('releasename')
    reportfile = request.GET.get('reportfile')
    print(scandatetime)
    print(solutionname)
    print(projectname)
    print(releasename)
    # Get POST data
    csv_content = request.body.decode('utf-8')

    # Convert comma-separated text to a CSV format
    reader = csv.reader(csv_content.splitlines(), delimiter=',')
    next(reader)
    csv_rows = list(reader)

    solution, _ = Solution.objects.get_or_create(name=solutionname)
    solution_id = solution.id

    release, _ = Release.objects.get_or_create(name=releasename)
    release_id = release.id

    project, _ = Project.objects.get_or_create(name=projectname)
    # project, _ = Project.objects.get(name=projectname)
    project_id = project.id

    result = Scan.objects.filter(
        Q(release_id=release_id) & Q(project_id=project_id)
    )

    if result.exists():
        print("Duplicate")
        # return JsonResponse({'status': 'There is already scan details are stored for this release and project '})
        return HttpResponseBadRequest("There is already scan details stored for this release and project", status=409)
    else:
        print("Entered else to create scan entry")
        scan = Scan(
            release_id=release_id,
            project_id=project_id,
            report_file=reportfile
        )

        scan.save()

        scan_id = scan.id

        for row in csv_rows:
            blackduck_component_id = row[1]
            blackduck_version_id = row[2]
            component_name = row[3]
            component_version = row[4]
            license_name = row[7]
            operational_risk = row[13]
            critical_vulnerability_count = row[31]
            high_vulnerability_count = row[32]
            medium_vulnerability_count = row[33]
            low_vulnerability_count = row[34]

            # # Check if the component exists in the Component table
            try:
                component = Component.objects.get(
                    name=component_name, version=component_version)
                print("Check to enterinto try")
            except Component.DoesNotExist:
                component = Component.objects.create(
                    blackduck_component_id=blackduck_component_id,
                    blackduck_version_id=blackduck_version_id,
                    name=component_name,
                    version=component_version)

            scan_detail = ScanDetails(
                scan_id=scan_id,
                component_id=component.id,
                critical_vulnerability_count=critical_vulnerability_count,
                high_vulnerability_count=high_vulnerability_count,
                medium_vulnerability_count=medium_vulnerability_count,
                low_vulnerability_count=low_vulnerability_count,
                operational_risk=operational_risk,
                license_name=license_name)
            scan_detail.save()

    return HttpResponse('Success!')


@csrf_exempt
def getcsv(request):

    # Call the sendcsv view using requests.get()
    response = requests.get('http://localhost:8000/sendcsv')
    # print(response)
    # scandatetime = request.GET.get('scandatetime')
    # solutionname = request.GET.get('solutionname')
    # projectname = request.GET.get('projectname')
    # releasename = request.GET.get('releasename')
    # data = json.loads(request.body)
    # Check if the request was successful
    if response.status_code == 200:
        response_data = response.json()
        scandatetime = response_data['scandatetime']
        solutionname = response_data['solutionname']
        projectname = response_data['projectname']
        releasename = response_data['releasename']
        reportfile = response_data['reportfile']
        data = response_data['data']
        print(scandatetime)
        print(solutionname)
        print(projectname)
        print(releasename)

        csv_string = '\n'.join(
            [','.join(['"{}"'.format(cell) for cell in row]) for row in data])
        csv_file = io.StringIO(csv_string)
        csv_reader = csv.reader(csv_file, quoting=csv.QUOTE_MINIMAL)
        next(csv_reader)

        solution, _ = Solution.objects.get_or_create(name=solutionname)
        solution_id = solution.id

        release, _ = Release.objects.get_or_create(name=releasename)
        release_id = release.id

        project, _ = Project.objects.get_or_create(name=projectname)
        # project, _ = Project.objects.get(name=projectname)
        project_id = project.id

        result = Scan.objects.filter(
            Q(release_id=release_id) & Q(project_id=project_id)
        )

        if result.exists():
            print("Duplicate")
            return JsonResponse({'status': 'There is already scan details are stored for this release and project '})
        else:
            scan = Scan(
                release_id=release_id,
                project_id=project_id,
                report_file=reportfile
            )

            scan.save()

            scan_id = scan.id

            for row in csv_reader:
                blackduck_component_id = row[1]
                blackduck_version_id = row[2]
                component_name = row[3]
                component_version = row[4]
                license_name = row[7]
                operational_risk = row[13]
                critical_vulnerability_count = row[31]
                high_vulnerability_count = row[32]
                medium_vulnerability_count = row[33]
                low_vulnerability_count = row[34]

                # # Check if the component exists in the Component table
            try:
                component = Component.objects.get(
                    name=component_name, version=component_version)
                print("Check to enterinto try")
            except Component.DoesNotExist:

                # component = None  # Assign None to component variable if it doesn't exist in the database

                #         # if component is None:
                #         #         # If not, insert the component into the Component table
                component = Component.objects.create(
                    blackduck_component_id=blackduck_component_id,
                    blackduck_version_id=blackduck_version_id,
                    name=component_name,
                    version=component_version)
            #         # If not, insert the component into the Component table
            #         # print("Entered into escept block")
            #         component = Component.objects.create(
            #             blackduck_component_id=blackduck_component_id,
            #             blackduck_version_id=blackduck_version_id,
            #             name=component_name,
            #             version=component_version
            #         )

            #         # Insert the row into the ScanDetails table with the component_id and other fields
            scan_detail = ScanDetails(
                scan_id=scan_id,
                component_id=component.id,
                critical_vulnerability_count=critical_vulnerability_count,
                high_vulnerability_count=high_vulnerability_count,
                medium_vulnerability_count=medium_vulnerability_count,
                low_vulnerability_count=low_vulnerability_count,
                operational_risk=operational_risk,
                license_name=license_name)
            scan_detail.save()

        print("Done")
        return JsonResponse({'status': 'success', 'message': 'CSV data processed'})
    else:
        return JsonResponse({'error': 'Failed to fetch CSV data'}, status=400)


# ----------------->>>>>>>>>>>>>>>>>>>>>>.>>...>>........--------------------------------------------
        # try:
        #     component = Component.objects.get(name=component_name, version=component_version)
        # except Component.DoesNotExist:
        #     # If not, insert the component into the Component table
        #     component = Component.objects.create(
        #         blackduck_component_id=row[0],
        #         blackduck_version_id=row[1],
        #         name=component_name,
        #         version=component_version
        #     )

        # # Insert the row into the ScanDetails table with the component_id and other fields
        # scan_detail = ScanDetails(
        #     scan_id=scan_id,
        #     component_id=component.id,
        #     critical_vulnerability_count=critical_vulnerability_count,
        #     high_vulnerability_count=high_vulnerability_count,
        #     medium_vulnerability_count=medium_vulnerability_count,
        #     low_vulnerability_count=low_vulnerability_count,
        #     operational_risk=operational_risk,
        #     license_name=license_name
        # )
        # scan_detail.save()
# --------------->>>>>>>>>>>>>>>>>>>>>>>>--------------------------------------------------------


def signout(request):
    logout(request)
    return redirect('/books/signin/')


@login_required
def home(request):
    return render(request, 'login.html')

# def home(request):
#     if request.user.is_authenticated:
#         return redirect('accounts/login/')
#     else:
#         return redirect('accounts/login/')


@csrf_protect
def login_attempt(request):
    if request.method == 'POST':
        print("nnnnn")
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        print(username+" "+password)
        if user is not None:
            if user.is_active == True:
                auth_login(request, user)
                return redirect('component')
            else:
                messages.success(request, 'Verify your email')
                return redirect('accounts/login')
        else:
            messages.error(request, 'No valid username or password')
            return redirect('/')

    return render(request, 'login.html')


def register_attempt(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        print(password1)

        try:
            if User.objects.filter(username=username).first():
                messages.success(request, 'Username is taken.')
                return redirect(reverse('register_attempt'))

            if User.objects.filter(email=email).first():
                messages.success(request, 'Email is taken.')
                return redirect(reverse('register_attempt'))
            if password1 != password2:
                messages.warning(request, 'Password does not match')
                return redirect(reverse('register_attempt'))
            user_obj = User.objects.create_user(
                username=username, email=email, password=password1)
            user_obj.is_active = False
            user_obj.save()

            send_email(user_obj)

            return redirect('token_send')

        except Exception as e:
            print(e)

    return render(request, 'register.html')


def success(request):
    return render(request, 'success.html')


def token_send(request):
    return render(request, 'token_send.html')


def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()

        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('/accounts/login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('/accounts/login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        return redirect('/')


def error_page(request):
    return render(request, 'error.html')


def send_mail_after_registration(email, token):
    try:
        subject = 'Your accounts need to be verified'
        message = f'Hi click the link to verify your account http://127.0.0.1:8080/verify/{token}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email, ]
        send_mail(subject, message, email_from, recipient_list)

    except Exception as e:
        return False

    return True


def main():
    with psycopg2.connect(conn_string) as connection:
        with connection.cursor() as cursor:
            cursor.execute("select * from solution")
            records = cursor.fetchall()

    return records


if __name__ == "__main__":
    main()


def index(request):
    # fields = ['id','name']
    # qs = Solution.objects.values_list(*fields)
    qs = Solution.objects.order_by('id').values_list('name', flat=True)
    context = {
        'Solution_List': qs
    }
    # return render(request, 'solutions.html', {'Solution_List': data})
    return render(request, 'solutions.html', context)


class DateTimeEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)


@login_required
def show_scan_detail(request):
    return render(request, 'scan_details_new.html')


@login_required
def scan_detail(request):

    if request.method == 'POST':
        project_filters = request.POST.getlist('projectFilters[]')
        name_filters = request.POST.getlist('nameFilters[]')
        solution_filters = request.POST.getlist('solutionFilters[]')
        release_filters = request.POST.getlist('releaseFilters[]')
        version_filters = request.POST.getlist('versionFilters[]')
        scan_filters = request.POST.getlist('scanFilters[]')
        print(solution_filters, project_filters, version_filters,
              scan_filters, name_filters, release_filters)
        scan_details = ScanDetails.objects.select_related('scan', 'component',
                                                          'scan__release', 'scan__project', 'scan__project__solution').all()
        # scan_details_filter = ScanDetails.objects.select_related('scan', 'component', 'scan__release', 'scan__project', 'scan__project__solution').filter(
        #     Q(scan__project__solution__name__in=solution_filters) & Q(scan__project__name__in=project_filters))
        # print(scan_details_filter)
        if version_filters:
            scan_details = scan_details.filter(
                component__version__in=version_filters)
        if name_filters:
            scan_details = scan_details.filter(
                component__name__in=name_filters)
        if scan_filters:
            scan_details = scan_details.filter(
                scan__scan_datetime__in=scan_filters)
        if release_filters:
            scan_details = scan_details.filter(
                scan__release__name__in=release_filters)
        if project_filters:
            scan_details = scan_details.filter(
                scan__project__name__in=project_filters)
        if solution_filters:
            scan_details = scan_details.filter(
                scan__project__solution__name__in=solution_filters)

        # if version_filters is not None:
        #     scan_details_filter = ScanDetails.objects.select_related('scan', 'component', 'scan__release', 'scan__project', 'scan__project__solution').filter(
        #         Q(component__version__in=version_filters))

        # filtered_scan_details_list = scan_details_list.filter(
        #     Q(scan__project__solution__name__in=solution_filters) &
        #     Q(scan__project__name__in=project_filters))
        scan_details_list = list(scan_details.values(
            'component__name', 'component__version', 'scan__scan_datetime', 'scan__release__name',
            'scan__project__name', 'scan__project__solution__name', 'critical_vulnerability_count',
            'high_vulnerability_count', 'medium_vulnerability_count', 'low_vulnerability_count'
        ))
        # print("San detail list")
        # print(scan_details_list)
        scan_details_dict_list = []
        for sd in scan_details_list:
            scan_details_dict = {
                'component_name': sd['component__name'],
                'component_version': sd['component__version'],
                'scan_datetime': sd['scan__scan_datetime'],
                'release_name': sd['scan__release__name'],
                'project_name': sd['scan__project__name'],
                'solution_name': sd['scan__project__solution__name'],
                'critical_count': sd['critical_vulnerability_count'],
                'high_count': sd['high_vulnerability_count'],
                'medium_count': sd['medium_vulnerability_count'],
                'low_count': sd['low_vulnerability_count']
            }
            scan_details_dict_list.append(scan_details_dict)
            # print("san detail list dict")
        # print(scan_details_dict_list)
        scan_details_json = json.dumps(
            scan_details_dict_list, cls=DateTimeEncoder)
        # print("code reacher")
        # print("scn json")
        # print(scan_details_json)
        return JsonResponse(json.loads(scan_details_json), safe=False)
    else:
        # sql1 = '''select license_name,critical_vulnerability_count,high_vulnerability_count,medium_vulnerability_count,low_vulnerability_count from scan_details ;'''
        # nm = "TVS"
        # sql2 = ''' SELECT C.name,version,R.name,S.name,scan_datetime,P.name,critical_vulnerability_count,high_vulnerability_count,medium_vulnerability_count,low_vulnerability_count FROM scan_details Scd,scan Sc,component C, release R,project P, solution S  WHERE Sc.id=Scd.scan_id AND C.id=Scd.component_id AND R.id=Sc.release_id AND P.id=Sc.project_id AND S.id= P.solution_id'''

        # cur.execute(sql2)
        # datas = cur.fetchall()

        # scan_details = ScanDetails.objects.select_related('scan', 'component',
        #                                                   'scan__release', 'scan__project', 'scan__project__solution').all()

        # # For multiple filters of solution
        # # solution_names = ['SP', 'DEF']
        # # project_names=['BLUE EYE','ABCTVS']

        # # scan_details_filter = ScanDetails.objects.select_related('scan', 'component', 'scan__release', 'scan__project', 'scan__project__solution').filter(
        # # Q(scan__project__solution__name__in=solution_names)& Q(scan__project__name__in=project_names))

        # scan_details_list = list(scan_details.values(
        #     'component__name', 'component__version', 'scan__scan_datetime', 'scan__release__name',
        #     'scan__project__name', 'scan__project__solution__name', 'critical_vulnerability_count',
        #     'high_vulnerability_count', 'medium_vulnerability_count', 'low_vulnerability_count'
        # ))

        # scan_details_dict_list = []
        # for sd in scan_details_list:
        #     scan_details_dict = {
        #         'component_name': sd['component__name'],
        #         'component_version': sd['component__version'],
        #         'scan_datetime': sd['scan__scan_datetime'],
        #         'release_name': sd['scan__release__name'],
        #         'project_name': sd['scan__project__name'],
        #         'solution_name': sd['scan__project__solution__name'],
        #         'critical_count': sd['critical_vulnerability_count'],
        #         'high_count': sd['high_vulnerability_count'],
        #         'medium_count': sd['medium_vulnerability_count'],
        #         'low_count': sd['low_vulnerability_count']
        #     }
        #     scan_details_dict_list.append(scan_details_dict)

        # #
        # scan_details_json = json.dumps(
        #     scan_details_dict_list, cls=DateTimeEncoder)
        # # print(scan_details_json)
        scan_details = ScanDetails.objects.select_related('scan', 'component',
                                                          'scan__release', 'scan__project', 'scan__project__solution').all()
        scan_details_list = list(scan_details.values(
            'component__name', 'component__version', 'scan__scan_datetime', 'scan__release__name',
            'scan__project__name', 'scan__project__solution__name', 'critical_vulnerability_count',
            'high_vulnerability_count', 'medium_vulnerability_count', 'low_vulnerability_count'
        ))
        scan_details_dict_list = []
        for sd in scan_details_list:
            scan_details_dict = {
                'component_name': sd['component__name'],
                'component_version': sd['component__version'],
                'scan_datetime': sd['scan__scan_datetime'],
                'release_name': sd['scan__release__name'],
                'project_name': sd['scan__project__name'],
                'solution_name': sd['scan__project__solution__name'],
                'critical_count': sd['critical_vulnerability_count'],
                'high_count': sd['high_vulnerability_count'],
                'medium_count': sd['medium_vulnerability_count'],
                'low_count': sd['low_vulnerability_count']
            }
            scan_details_dict_list.append(scan_details_dict)

        scan_details_json = json.dumps(
            scan_details_dict_list, cls=DateTimeEncoder)
        # print("printing in the scan detail")
        # print(scan_details_json)
        print("code reacher")
        return JsonResponse(json.loads(scan_details_json), safe=False)

    # return JsonResponse(scan_details_dict_list, status=200)


def filterscandetails(request):

    if request.method == 'POST':
        fname_filters = request.POST.getlist('nameFilters[]')
        project_filters = request.POST.getlist('projectFilters[]')
        solution_filters = request.POST.getlist('solutionFilters[]')
        release_filters = request.POST.getlist('releaseFilters[]')
        version_filters = request.POST.getlist('versionFilters[]')
        scan_filters = request.POST.getlist('scanFilters[]')

        scan_details = ScanDetails.objects.select_related(
            'scan', 'component', 'scan__release', 'scan__project', 'scan__project__solution')
        
# Apply name filters on entire queryset        
        if fname_filters:
            scan_details = scan_details.filter(
                Q(component__name__in=fname_filters))

# Apply version filters on the name filtered queryset
        version_filtered_scan_details = scan_details
        if version_filters:
            version_filtered_scan_details = version_filtered_scan_details.filter(
                Q(component__version__in=version_filters))

# Apply release filters on the version filtered queryset
        release_filtered_scan_details = version_filtered_scan_details
        if release_filters:
            release_filtered_scan_details = release_filtered_scan_details.filter(
                Q(scan__release__name__in=release_filters))

# Apply solution filters on the release filtered queryset
        solution_filtered_scan_details = release_filtered_scan_details
        if solution_filters:
            solution_filtered_scan_details = solution_filtered_scan_details.filter(
                Q(scan__project__solution__name__in=solution_filters))

# Apply scan filters on the solution filtered queryset
        scan_filtered_scan_details = solution_filtered_scan_details
        print("pritinging above scanfilterapply")
        print(scan_filtered_scan_details)
        if scan_filters:
            scan_datetime_str = scan_filters[0]
            scan_datetime = datetime.strptime(scan_datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
            formatted_datetime_str = scan_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
            formatted_datetime_str = formatted_datetime_str[:-3]  # Remove the last three digits for milliseconds
            # scan_filtered_scan_details = scan_filtered_scan_details.filter(
            #     Q(scan__scan_datetime__in=scan_filters))
            scan_filtered_scan_details = scan_filtered_scan_details.filter(scan__scan_datetime__contains=formatted_datetime_str)
            print("scandatime")
            print(formatted_datetime_str)
            print("printing below scn filter")
            print(scan_filtered_scan_details)

# Apply project filters on the scan filtered queryset
        final_filtered_scan_details = scan_filtered_scan_details
        if project_filters:
            final_filtered_scan_details = final_filtered_scan_details.filter(
                Q(scan__project__name__in=project_filters))

        scan_details_list = list(final_filtered_scan_details.values(
            'component__name', 'component__version', 'scan__scan_datetime', 'scan__release__name',
            'scan__project__name', 'scan__project__solution__name', 'critical_vulnerability_count',
            'high_vulnerability_count', 'medium_vulnerability_count', 'low_vulnerability_count'
        ))

        scan_details_dict_list = []
        for sd in scan_details_list:
            scan_details_dict = {
                'component_name': sd['component__name'],
                'component_version': sd['component__version'],
                'scan_datetime': sd['scan__scan_datetime'],
                'release_name': sd['scan__release__name'],
                'project_name': sd['scan__project__name'],
                'solution_name': sd['scan__project__solution__name'],
                'critical_count': sd['critical_vulnerability_count'],
                'high_count': sd['high_vulnerability_count'],
                'medium_count': sd['medium_vulnerability_count'],
                'low_count': sd['low_vulnerability_count']
            }
            scan_details_dict_list.append(scan_details_dict)
        scan_details_json = json.dumps(
            scan_details_dict_list, cls=DateTimeEncoder)
        scans_details_json_new = json.loads(scan_details_json)

        versions_queryset = Component.objects.filter(
            name__in=fname_filters).values_list('version', flat=True)
        releases_queryset = Component.objects.filter(name__in=fname_filters).values_list(
            'scandetails__scan__release__name', flat=True)
        solution_queryset = Component.objects.filter(name__in=fname_filters).values_list(
            'scandetails__scan__project__solution__name', flat=True)
        scan_queryset = Component.objects.filter(name__in=fname_filters).values_list(
            'scandetails__scan__scan_datetime', flat=True)
        project_queryset = Component.objects.filter(name__in=fname_filters).values_list(
            'scandetails__scan__project__name', flat=True)

        print("printing in filtersname scan")
        # print(scans_details_json_new)
        versions = list(versions_queryset)
        releases = list(releases_queryset)
        solutions = list(solution_queryset)
        scans_unmodified = list(scan_queryset)
        projects = list(project_queryset)

        scans_list = json.dumps(scans_unmodified, cls=DateTimeEncoder)
        scans = json.loads(scans_list)

        data = {
            'versions': versions,
            'releases': releases,
            'solutions': solutions,
            'scans': scans,
            'projects': projects,
            'filteredscan': scans_details_json_new,

        }
        return JsonResponse(data, safe=False)


# -------->     Working code starts

        # if searchname is None:
        #     print("fname is empty")
        # scan_details = ScanDetails.objects.select_related('scan', 'component',  'scan__release', 'scan__project', 'scan__project__solution').filter(
        #     Q(component__name__in=searchname))

        # scan_details_list = list(scan_details.values(
        #     'component__name', 'component__version', 'scan__scan_datetime', 'scan__release__name',
        #     'scan__project__name', 'scan__project__solution__name', 'critical_vulnerability_count',
        #     'high_vulnerability_count', 'medium_vulnerability_count', 'low_vulnerability_count'
        # ))
        # scan_details_dict_list = []
        # for sd in scan_details_list:
        #     scan_details_dict = {
        #         'component_name': sd['component__name'],
        #         'component_version': sd['component__version'],
        #         'scan_datetime': sd['scan__scan_datetime'],
        #         'release_name': sd['scan__release__name'],
        #         'project_name': sd['scan__project__name'],
        #         'solution_name': sd['scan__project__solution__name'],
        #         'critical_count': sd['critical_vulnerability_count'],
        #         'high_count': sd['high_vulnerability_count'],
        #         'medium_count': sd['medium_vulnerability_count'],
        #         'low_count': sd['low_vulnerability_count']
        #     }
        #     scan_details_dict_list.append(scan_details_dict)
        # scan_details_json = json.dumps(
        #     scan_details_dict_list, cls=DateTimeEncoder)
        # scans_details_json_new = json.loads(scan_details_json)

        # versions_queryset = Component.objects.filter(
        #     name__in=searchname).values_list('version', flat=True)
        # releases_queryset = Component.objects.filter(name__in=searchname).values_list(
        #     'scandetails__scan__release__name', flat=True)
        # solution_queryset = Component.objects.filter(name__in=searchname).values_list(
        #     'scandetails__scan__project__solution__name', flat=True)
        # scan_queryset = Component.objects.filter(name__in=searchname).values_list(
        #     'scandetails__scan__scan_datetime', flat=True)
        # project_queryset = Component.objects.filter(name__in=searchname).values_list(
        #     'scandetails__scan__project__name', flat=True)

        # print("printing in filtersname scan")
        # # print(scans_details_json_new)
        # versions = list(versions_queryset)
        # releases = list(releases_queryset)
        # solutions = list(solution_queryset)
        # scans_unmodified = list(scan_queryset)
        # projects = list(project_queryset)

        # scans_list = json.dumps(scans_unmodified, cls=DateTimeEncoder)
        # scans = json.loads(scans_list)
        # # print(searchname)
        # # print(versions)
        # # print(releases)
        # # print(solutions)
        # # print(scans)
        # # print(projects)

        # data = {
        #     'versions': versions,
        #     'releases': releases,
        #     'solutions': solutions,
        #     'scans': scans,
        #     'projects': projects,
        #     'filteredscan': scans_details_json_new
        # }
        # return JsonResponse(data, safe=False)

# -------->     Working code ends


def searchrecords(request):
    if request.method == 'POST':
        searchname = request.POST['search']
        scan_details = ScanDetails.objects.select_related('scan', 'component', 'scan__release', 'scan__project', 'scan__project__solution').filter(
            Q(component__name__icontains=searchname))
        scan_details_list = list(scan_details.values(
            'component__name', 'component__version', 'scan__scan_datetime', 'scan__release__name',
            'scan__project__name', 'scan__project__solution__name', 'critical_vulnerability_count',
            'high_vulnerability_count', 'medium_vulnerability_count', 'low_vulnerability_count'
        ))
        # print("San detail list")
        # print(scan_details_list)
        scan_details_dict_list = []
        for sd in scan_details_list:
            scan_details_dict = {
                'component_name': sd['component__name'],
                'component_version': sd['component__version'],
                'scan_datetime': sd['scan__scan_datetime'],
                'release_name': sd['scan__release__name'],
                'project_name': sd['scan__project__name'],
                'solution_name': sd['scan__project__solution__name'],
                'critical_count': sd['critical_vulnerability_count'],
                'high_count': sd['high_vulnerability_count'],
                'medium_count': sd['medium_vulnerability_count'],
                'low_count': sd['low_vulnerability_count']
            }
            scan_details_dict_list.append(scan_details_dict)
        scan_details_json = json.dumps(
            scan_details_dict_list, cls=DateTimeEncoder)
        scans_details_json_new = json.loads(scan_details_json)

        names = [item['component__name'] for item in scan_details_list]
        versions = [item['component__version'] for item in scan_details_list]
        releases = [item['scan__release__name'] for item in scan_details_list]
        solutions = [item['scan__project__solution__name']
                     for item in scan_details_list]
        scans_unmodified = [item['scan__scan_datetime']
                            for item in scan_details_list]
        projects = [item['scan__project__name'] for item in scan_details_list]

        scans_list = json.dumps(scans_unmodified, cls=DateTimeEncoder)
        scans = json.loads(scans_list)

        data = {
            'names': names,
            'versions': versions,
            'releases': releases,
            'solutions': solutions,
            'scans': scans,
            'projects': projects,
            'filteredscan': scans_details_json_new
        }
        return JsonResponse(data, safe=False)
        # return JsonResponse(json.loads(scan_details_json), safe=False)


def getSolutions(request):
    if request.method == "GET":
        solutions = Solution.objects.exclude(name__isnull=True).\
            exclude(name__exact='').order_by(
                'name').values_list('name').distinct()
        solution = [i[0] for i in list(solutions)]
        data = {
            "solution": solution,
        }
        # print(data)
    return JsonResponse(data, status=200)


def getVersions(request):
    if request.method == "GET":
        component = Component.objects.values_list('version', flat=True)
        component = [i for i in list(component)]
        data = {
            "version": component,
        }
        # print(data)
    return JsonResponse(data, status=200)


def getReleases(request):
    if request.method == "GET":
        release = Release.objects.values_list('name', flat=True)
        release = [i for i in list(release)]
        data = {
            "release": release,
        }
        # print(data)
    return JsonResponse(data, status=200)


def getScans(request):
    if request.method == "GET":
        scan = Scan.objects.values_list('scan_datetime', flat=True)
        scan = [i for i in list(scan)]
        data = {
            "scan": scan,
        }
        # print(data)
    return JsonResponse(data, status=200)


def getProjects(request):
    if request.method == "GET":
        scan = Project.objects.values_list('name', flat=True)
        scan = [i for i in list(scan)]
        data = {
            "project": scan,
        }
        # print(data)
    return JsonResponse(data, status=200)


def getNames(request):
    if request.method == "GET":
        scan = Component.objects.values_list('name', flat=True)
        scan = [i for i in list(scan)]
        data = {
            "name": scan,
        }
        # print(data)
    return JsonResponse(data, status=200)


def get_updated_filter_options(request):
    selected_filter = request.GET.get('selectedFilter')
    # Determine the options for other filters based on the selected filter
    # Fetch the updated options from the database or any other data source
    # Create a dictionary of filter options
    updated_options = {
        'nameFilters': ['Name 1', 'Name 2', 'Name 3'],
        'versionFilters': ['Version 1', 'Version 2', 'Version 3'],
        'releaseFilters': ['Release 1', 'Release 2', 'Release 3'],
        'solutionFilters': ['Solution 1', 'Solution 2', 'Solution 3'],
        'scanFilters': ['Scan 1', 'Scan 2', 'Scan 3'],
        'projectFilters': ['Project 1', 'Project 2', 'Project 3']
    }
    return JsonResponse(updated_options)


@login_required
def components(request):

    return render(request, 'components.html')


def components_manage(request):
    return render(request, 'solutionproject.html')


def add_solution(request):
    if request.method == "POST":
        if request.POST['addsolution'] != '' and request.POST['addsolution'] is not None:
            addsolutions = request.POST['addsolution']
            print(addsolutions)
            Solution.objects.create(name=request.POST['addsolution'])
    return redirect(index)


def edit_solution(request):
    if request.method == "POST":
        # if request.POST['editsolution'] != '' and request.POST['editsolution'] is not None:
        if request.POST['editsol'] != '' and request.POST['editsol'] is not None:
            if request.POST['editname'] != '' and request.POST['editname'] is not None:
                editsol = request.POST.get('editsol')
                editname = request.POST.get('editname')
                se = Solution.objects.filter(
                    name__exact=editsol).update(name=editname)
                # del.name=editname
                # se=Solution.objects.filter(name__exact=editsol).values_list('name', flat=True)
                # print(se)
                print(editsol)
                print(editname)
    return redirect(index)


def delete_solution(request):
    if request.method == "POST":
        if request.POST['sol'] != '' and request.POST['sol'] is not None:
            delsol = request.POST['sol']
            print(delsol)
            Solution.objects.filter(name__exact=delsol).delete()
    return redirect(index)


def showprojects(request):

    if request.method == 'POST':
        project_name = request.POST.get('projectName')
        selected_solution_id = request.POST.get('selectedSolution')
        blackduck_projectName = request.POST.get('blackduckprojectName')
        # Check if the solution ID is valid
        try:
            selected_solution = Solution.objects.get(name=selected_solution_id)
            selected_solution_id = selected_solution.id
        except Solution.DoesNotExist:
            response_data = {'success': False,
                             'message': 'Invalid solution selected.'}
            return JsonResponse(response_data)

        # Create a new Project instance
        new_project = Project.objects.create(
            name=project_name,
            solution=selected_solution,
            # Set the blackduck_project_name value as per your requirements
            blackduck_project_name=blackduck_projectName,
            auto_monitor=False  # Set the auto_monitor value as per your requirements
        )

        # Return a JSON response indicating the success of the operation
        response_data = {'success': True,
                         'message': 'Project added successfully.'}
        return JsonResponse(response_data)

    if request.method == 'PUT':

        project_name = request.GET.get('selectedProjectNames')
        selected_solution_name = request.GET.get('selectedSolutionNames')
        new_projectname = request.GET.get('newProjectName')

        # Check if the project ID is valid
        try:
            selected_project = Project.objects.get(name=project_name)
            selected_solution = Solution.objects.get(
                name=selected_solution_name)
            # selected_solution_id = selected_solution.id
        except Project.DoesNotExist:
            response_data = {'success': False,
                             'message': 'Invalid project ID.'}
            return JsonResponse(response_data)
        print(selected_project)

        # Update the project details
        selected_project.name = new_projectname
        selected_project.solution = selected_solution
        selected_project.blackduck_project_name = selected_project.blackduck_project_name
        selected_project.save()

        # Return a JSON response indicating the success of the operation
        response_data = {'success': True,
                         'message': 'Project updated successfully.'}
        return JsonResponse(response_data)

    elif request.method == 'DELETE':
        selected_ProjectName = request.GET.get('selectedProjectName')
        selected_SolutionName = request.GET.get('selectedSolutionName')

        print(selected_ProjectName)
        try:
            selected_project = Project.objects.get(name=selected_ProjectName)
        except Project.DoesNotExist:
            response_data = {'success': False,
                             'message': 'Invalid project name.'}
            return JsonResponse(response_data)

        # Check if the project's solution name matches the selected solution name
        if selected_project.solution.name == selected_SolutionName:
            # Delete the project
            selected_project.delete()
            response_data = {'success': True,
                             'message': 'Project deleted successfully.'}
        else:
            response_data = {'success': False,
                             'message': 'Solution name does not match.'}

        return JsonResponse(response_data)

    else:
        project_solution = Project.objects.select_related('solution')
        project_solution_list = list(project_solution.values(
            'name', 'solution__name'))

        scan_details_dict_list = []
        for sd in project_solution_list:
            project_details_dict = {
                'name': sd['name'],
                'solution_name': sd['solution__name'],
            }
            scan_details_dict_list.append(project_details_dict)
        print(scan_details_dict_list)
        return JsonResponse({'scan_details': scan_details_dict_list})


def showrelease(request):

    if request.method == 'POST':
        release_name = request.POST.get('releaseName')
        release_date = request.POST.get('releaseDate')

        # Create a new release object
        new_release = Release(name=release_name, release_date=release_date)
        new_release.save()

        # Return a JSON response indicating the success of the operation
        response_data = {'success': True,
                         'message': 'Release created successfully.'}
        return JsonResponse(response_data)

    if request.method == 'PUT':

        project_name = request.GET.get('selectedProjectNames')
        selected_solution_name = request.GET.get('selectedSolutionNames')
        new_projectname = request.GET.get('newProjectName')

        # Check if the project ID is valid
        try:
            selected_project = Project.objects.get(name=project_name)
            selected_solution = Solution.objects.get(
                name=selected_solution_name)
            # selected_solution_id = selected_solution.id
        except Project.DoesNotExist:
            response_data = {'success': False,
                             'message': 'Invalid project ID.'}
            return JsonResponse(response_data)
        print(selected_project)

        # Update the project details
        selected_project.name = new_projectname
        selected_project.solution = selected_solution
        selected_project.blackduck_project_name = selected_project.blackduck_project_name
        selected_project.save()

        # Return a JSON response indicating the success of the operation
        response_data = {'success': True,
                         'message': 'Project updated successfully.'}
        return JsonResponse(response_data)

    elif request.method == 'DELETE':
        selected_ReleaseName = request.GET.get('selectedReleaseName')
        selected_ReleaseDate = request.GET.get('selectedReleaseDate')
        print(selected_ReleaseDate)

        try:
            selected_release = Release.objects.get(name=selected_ReleaseName)
        except Release.DoesNotExist:
            response_data = {'success': False,
                             'message': 'Invalid Release name.'}
            return JsonResponse(response_data)

            # Check if the project's release date matches the selected release date
        if selected_release.release_date == datetime.strptime(selected_ReleaseDate, '%Y-%m-%d').date():
            # Delete the release
            selected_release.delete()
            response_data = {'success': True,
                             'message': 'Release deleted successfully.'}
        else:
            response_data = {
                'success': False, 'message': 'Release date doesnt match the selected date.'}

        return JsonResponse(response_data)

    else:
        releases = Release.objects.all()
        release_list = []
        for release in releases:
            release_dict = {
                'name': release.name,
                # Convert release_date to a string format
                'release_date': release.release_date.strftime('%Y-%m-%d')
            }
            release_list.append(release_dict)

        print(release_list)
        return JsonResponse({'release_list': release_list})


def release(request):
    return render(request, 'releases.html')


def project(request):

    return render(request, 'projects.html')

    #     scan_details_json = json.dumps(
    #         scan_details_dict_list, cls=DateTimeEncoder)
    # print(scan_details_json)
    # return JsonResponse(json.loads(scan_details_json), safe=False)

    # qs = Project.objects.order_by('id').all()
    data = Project.objects.values_list('name', flat=True)

    # # data = serializers.serialize("json", Project.objects.all().order_by('id'))
    project = [i for i in list(data)]
    data = {
        "project": project,
    }
    print(data)
    return render(request, 'projects.html', data)


def sample(request):
    return render(request, 'djangopyscandetail.html')


def projectfilterdropdown(request):
    if request.method == "GET":
        selected_solution = request.GET.get('solution', None)

    # Filter projects based on selected solution
    if selected_solution:
        projects = Project.objects.filter(
            solution=selected_solution).values_list('name', flat=True)
    else:
        projects = Project.objects.values_list('name', flat=True)
    print("Printinf selected solution")
    print(selected_solution)
    # Convert queryset to list
    projects = list(projects)

    # Prepare response data
    data = {
        "project": projects,
    }

    # Return JSON response
    return JsonResponse(data, status=200)


@api_view(['GET'])
def irrigationsAPI(request):
    #     products = IrrigationDetails.objects.all().order_by('irr_id')
    #     serializer = IrrigationDetailsSerializer(products, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    pass


@api_view(['GET'])
def irrigationsDetailsAPI(request, id):
    # temp_id=uuid.UUID(str(id))
    # product = get_object_or_404(IrrigationDetails, irr_id=temp_id)
    # serializer = IrrigationDetailsSerializer(product, many=False)
    # return Response(serializer.data, status=status.HTTP_200_OK)
    pass


@api_view(['POST'])
def addIrrigationsAPI(request):
    # serializer = IrrigationDetailsSerializer(data=request.data)
    # if serializer.is_valid():
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    pass


@api_view(['DELETE'])
def deleteIrrigationsAPI(request, id):
    # temp_id=uuid.UUID(str(id))
    # product = get_object_or_404(IrrigationDetails,irr_id=temp_id)
    # if product is not None:
    #   product.delete()
    #   return Response('Product successfully Deleted!', status=status.HTTP_200_OK)
    # return Response("That Product Doesn't Exists!", status=status.HTTP_204_NO_CONTENT)
    pass
