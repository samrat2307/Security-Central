from django.contrib import admin
from django.urls import path
from .views import *
from django.views.generic import TemplateView
# from . import views

urlpatterns = [
    
    # path('',  home, name="home"),
    path('',  home, name="home"),
    path('accounts/register/', register_attempt, name="register_attempt"),
    path('accounts/login/', login_attempt, name="login_attempt"),
    path('token', token_send, name="token_send"),
    path('success', success, name='success'),
    path('verify/<auth_token>', verify, name="verify"),
    path('error', error_page, name="error"),
    # path('welcome' , index , name='welcome'),
    
    path('components/showviewstatus', show_scan_detail, name='showscandetail'),
    path('components/manage/solution', index, name='solution'),
    # above for all sol main
    path('components', components, name='component'),

    # path('submitsolution', submit_solution, name='submitsolution'),
    # # above for insertion

    path('addsolution', add_solution, name='addsolution'),
    # above for insertion check
    path('deletesolution', delete_solution, name='deletesolution'),
    # above for deletesolution
    path('editsolution', edit_solution, name='editsolution'),
    # above for edit solution
    path('components/manage', components_manage, name='solutionproject'),
    path('components/manage/project', project, name='project'),
    path('components/manage/release', release, name='release'),
    path('showrelease', showrelease, name='showrelease'),
    path('showprojects', showprojects, name='showproject'),
    path('ajax/components/viewstatus', scan_detail, name='scandetail'),
    path('ajax/searchrecords', searchrecords, name='searchrecords'),
    path('sol',getSolutions , name='solutions'),
    path('ajax/versions',getVersions , name='versions'),
    path('ajax/releases',getReleases , name='releases'),
    path('ajax/scans',getScans , name='scans'),    
    path('ajax/projects',getProjects , name='projects'),    
    path('ajax/names',getNames , name='names'),   
    path('filterscandetails',filterscandetails , name='filterscandetails'),
    path('get_updated_filter_options',get_updated_filter_options , name='get_updated_filter_options'), 
    path('ajax/projects/fiterdropdown',projectfilterdropdown , name='projectfilterdropdown'),
    path('sendcsv',sendcsv , name='sendcsv'), 
    path('getcsv',getcsv , name='getcsv'),
    path('storescan',storescan,name='storescan')    
   


]
