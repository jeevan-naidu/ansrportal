from django.shortcuts import render
from constants import WORKFLOW_APPS
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.http import Http404
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.renderers import TemplateHTMLRenderer


from models import get_app_detail, get_queryset, get_role, update_process, is_final


def process(request):
    return render(request, 'templates/landingpage.html', {'taskprocess': WORKFLOW_APPS})


class ProcessListView(generics.ListAPIView, LoginRequiredMixin):

    def list(self, request, **kwargs):
        config = get_app_detail(request, **kwargs)
        model = config.PROCESS[config.INITIAL]['model']
        serializer = config.PROCESS[config.INITIAL]['serializer']
        self.queryset = queryset = model.objects.filter(is_active=True).exclude(process_status='Completed',
                                                                                request_status__in=['Completed',
                                                                                                    'Rolled Back'])
        serializer = serializer(queryset, many=True)
        return Response(serializer.data)


class StartProcess(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'templates/process_form.html'

    def get(self, request, **kwargs):
        config = get_app_detail(request, **kwargs)
        serializer = config.PROCESS[config.INITIAL]['serializer']
        return Response({'serializer': serializer()})

    def post(self, request, **kwargs):
        config = get_app_detail(request, **kwargs)
        process_serializer = config.PROCESS[config.INITIAL]['serializer']
        serializer = process_serializer(data=request.data)
        if serializer.is_valid():
            serializer.saveas(request)
            return Response({'serializer': serializer}, status.HTTP_201_CREATED)
        return Response(status.HTTP_400_BAD_REQUEST)


class ProcessUpdate(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'templates/process_update.html'

    def get_object(self, request, pk, **kwargs):
        try:
            config = get_app_detail(request, **kwargs)
            model = config.PROCESS[config.INITIAL]['model']
            return get_object_or_404(model, pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, **kwargs):
        config = get_app_detail(request, **kwargs)
        process_serializer = config.PROCESS[config.INITIAL]['serializer']
        activity = self.get_object(request, pk, **kwargs)
        serializer = process_serializer(activity)
        return Response({'serializer': serializer, 'pk': pk})

    def post(self, request, pk, **kwargs):
        config = get_app_detail(request, **kwargs)
        process_serializer = config.PROCESS[config.INITIAL]['serializer']
        activity = self.get_object(request, pk, **kwargs)
        serializer = process_serializer(activity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'serializer': serializer, 'pk': pk})
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, **kwargs):
        activity = self.get_object(request, pk, **kwargs)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApproveListView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'templates/approval.html'

    def get(self, request, **kwargs):
        # import ipdb; ipdb.set_trace()
        config = get_app_detail(request, **kwargs)
        transition = config.PROCESS[config.INITIAL]['transitions']
        serializer = config.PROCESS[transition[0]]['serializer']
        modal = config.PROCESS[config.INITIAL]['model']
        queryset = get_queryset(request, **kwargs)
        abstract_fields = ['creation_date', 'last_updated', 'is_active', 'process_status', 'transaction']
        fields = [f.name for f in modal._meta.get_fields()]
        fields = filter(lambda x: x not in abstract_fields, fields)
        fields.sort(reverse=True)
        serializer = serializer()
        return Response({'queryset': queryset, 'serializer': serializer, 'fields': fields})

    def post(self, request, **kwargs):
        pk = request.POST['id']
        action = request.POST['action']
        config = get_app_detail(request, **kwargs)
        transition = config.PROCESS[config.INITIAL]['transitions']
        serializer = config.PROCESS[transition[0]]['serializer']
        model = config.PROCESS[config.INITIAL]['model']
        serialized_data = serializer(data=request.POST)
        if serialized_data.is_valid():
            process_request = model.objects.get(pk=pk)
            role = get_role(config, action, process_request.role)
            final = is_final(config, process_request.role)
            update_process(process_request, role, action, final)
            serialized_data.save_as(role, request, pk, action)
        modal = config.PROCESS[config.INITIAL]['model']
        queryset = get_queryset(request, **kwargs)
        abstract_fields = ['creation_date', 'last_updated', 'is_active', 'process_status', 'transaction']
        fields = [f.name for f in modal._meta.get_fields()]
        fields = filter(lambda x: x not in abstract_fields, fields)
        fields.sort(reverse=True)
        return Response({'queryset': queryset, 'serializer': serializer, 'fields': fields})










