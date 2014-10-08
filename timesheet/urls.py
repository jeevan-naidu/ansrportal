from django.conf.urls import patterns, url
from timesheet import views
from timesheet.forms import ProjectBasicInfoForm, ProjectTeamForm, \
    ProjectMilestoneForm, snapshotForm
from django.forms.formsets import formset_factory

urlpatterns = patterns(u'',
                       url(r'^add$', views.Timesheet, name=u'timesheet'),
                       url(r'^project/add$',
                           views.CreateProjectWizard.as_view([
                               ProjectBasicInfoForm,
                               formset_factory(
                                   ProjectTeamForm,
                                   extra=2
                               ),
                               formset_factory(ProjectMilestoneForm, extra=2)
                           ]),
                           name=u'createproject'),
                       url(r'^logout/$', views.Logout, name=u'logout'),
                       url(r'^$', views.index, name=u'index'),
                       )
