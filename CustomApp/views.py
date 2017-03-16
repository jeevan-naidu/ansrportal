from django.shortcuts import render
from constants import WORKFLOW_APPS
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser

from models import get_app_detail,\
    manager_queryset,\
    get_role,\
    update_process,\
    is_final,\
    get_app_name,\
    get_process_transactions,\
    user_queryset


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
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]


    def get(self, request, **kwargs):
        config = get_app_detail(request, **kwargs)
        serializer = config.PROCESS[config.INITIAL]['serializer']
        app_name = get_app_name(request, **kwargs)
        config = get_app_detail(request, **kwargs)
        transition = config.PROCESS[config.INITIAL]['transitions']
        modal = config.PROCESS[config.INITIAL]['model']
        transaction_modal = config.PROCESS[transition[0]]['model'].__name__.lower()
        queryset = user_queryset(request, config)
        fields = get_process_transactions(modal, transaction_modal, config.DETAIL, "user")
        return Response({'queryset': queryset, 'serializer': serializer, 'fields': fields, 'app_name': app_name}, template_name = 'templates/user_dashboard.html')

    def post(self, request, **kwargs):
        config = get_app_detail(request, **kwargs)
        app_name = get_app_name(request, **kwargs)
        process_serializer = config.PROCESS[config.INITIAL]['serializer']
        serializer = process_serializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save_as(request)
            except:
                return Response({'serializer': serializer},status.HTTP_400_BAD_REQUEST)

            return Response({'record_added': True}, status.HTTP_201_CREATED)
        return render(request, 'form_errors.html', {'serializer': serializer, 'record_added': False, 'app_name': app_name})

class GetProcess(APIView):
    """
    Get Process details
    """
    parser_classes = (FileUploadParser,MultiPartParser, FormParser)
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'templates/update_form.html'

    def get_object(self, pk, model):
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise Http404

    def get_process(self, request, **kwargs):
        config = get_app_detail(request, **kwargs)
        serializer = config.PROCESS[config.INITIAL]['serializer']
        modal = config.PROCESS[config.INITIAL]['model']
        return serializer, modal

    def get(self, request, pk, **kwargs):
        app_name = get_app_name(request, **kwargs)
        process = self.get_process(request, **kwargs)
        process_object = self.get_object(pk, process[1])
        serializer = process[0](process_object, partial=True)
        return Response({"serializer":serializer,
                         "pk":pk,
                         "app_name":app_name},)



class UpdateProcess(APIView):
    """
    Retrieve, update or delete a process instance
    """
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def get_object(self, pk, model):
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise Http404

    def get_process(self, request, **kwargs):
        config = get_app_detail(request, **kwargs)
        serializer = config.PROCESS[config.INITIAL]['serializer']
        modal = config.PROCESS[config.INITIAL]['model']
        return serializer, modal


    def put(self, request, pk, **kwargs):
        process = self.get_process(request, **kwargs)
        app_name = get_app_name(request, **kwargs)
        process_object = self.get_object(pk, process[1])
        serializer = process[0](process_object, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'record_added': True}, status.HTTP_201_CREATED)
        return render(request, 'update_form.html',
                          {'serializer': serializer, 'app_name': app_name, 'pk':pk})

    def delete(self, request, pk, **kwargs):
        process = self.get_process(request, **kwargs)
        process_object = self.get_object(pk, process[1])
        process_object.process_status = "Rolled Back"
        process_object.request_status = "Withdrawn"
        process_object.is_active = False
        process_object.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProcessApproval(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'templates/approval_dashboard.html'

    def get_object(self, request, pk, **kwargs):
        try:
            config = get_app_detail(request, **kwargs)
            model = config.PROCESS[config.INITIAL]['model']
            return get_object_or_404(model, pk=pk)
        except:
            raise Http404

    def get_process_detail(self, request, **kwargs):
        config = get_app_detail(request, **kwargs)
        process_details = list()
        process_details.append(config.INITIAL)
        transitions = config.PROCESS[config.INITIAL]['transitions']
        while transitions[0]:
            process_details.append(transitions[0])
            transitions = config.PROCESS[transitions[0]]['transitions']
        return process_details

    def get_object_detail(self, request, pk, **kwargs):
        try:
            config = get_app_detail(request, **kwargs)
            display_fields = config.DETAIL
            modal = config.PROCESS[config.INITIAL]['model']
            process = get_object_or_404(modal, pk=pk)
            fields = [f.name for f in modal._meta.get_fields()]
            fields = filter(lambda x: x in display_fields, fields)
            fields_data = list()
            for field in fields:
                fields_data.append(getattr(process, field))
            return zip(fields, fields_data)
        except:
            pass

    def process_status_detail(self, request, pk, **kwargs):
        try:
            config = get_app_detail(request, **kwargs)
            modal = config.PROCESS[config.INITIAL]['model']
            process = get_object_or_404(modal, pk=pk)
            current_role = process.role
            action_taken_for_roles = list()
            roles_action_detail = list()
            transitions = config.PROCESS[config.INITIAL]['transitions']
            roles_selected = config.PROCESS[config.INITIAL]['role']
            process_role = config.PROCESS[transitions[0]]['role']
            action_taken_for_roles.append(roles_selected)
            roles_action_detail.append(config.PROCESS[config.INITIAL]['serializer'](process))
            while transitions[0]:
                roles_selected = config.PROCESS[transitions[0]]['role']
                transitions = config.PROCESS[transitions[0]]['transitions']
                if roles_selected == current_role:
                    if is_final(config, roles_selected):
                        process_role = config.PROCESS[transitions[0]]['role']
                    else:
                        next_role = config.PROCESS[transitions[0]]['role']
                        process_role = next_role

                action_taken_for_roles.append(roles_selected)
                transactions = config.PROCESS[config.PROCESS[config.INITIAL]['transitions'][0]]['serializer'].\
                    transactions(pk, roles_selected)
                roles_action_detail.append(transactions)

            process_status = zip(action_taken_for_roles, roles_action_detail)

            return [process_status, process_role]
        except:
            pass

    def get(self, request, pk, **kwargs):
        app_name = get_app_name(request, **kwargs)
        config = get_app_detail(request, **kwargs)
        process_serializer = config.PROCESS[config.INITIAL]['serializer']
        activity = self.get_object(request, pk, **kwargs)
        serializer = process_serializer(activity)
        process_detail = self.get_process_detail(request, **kwargs)
        object_detail = self.get_object_detail(request, pk, **kwargs)
        process_status_detail = self.process_status_detail(request, pk, **kwargs)
        return Response({'serializer': serializer,
                         'pk': pk,
                         'process_detail': process_detail,
                         'object_detail': object_detail,
                         'process_status_detail': process_status_detail[0],
                         'current_role': process_status_detail[1],
                         'app_name': app_name})

    def post(self, request, pk, **kwargs):
        app_name = get_app_name(request, **kwargs)
        config = get_app_detail(request, **kwargs)
        transition = config.PROCESS[config.INITIAL]['transitions']
        serializer = config.PROCESS[transition[0]]['serializer']
        model = config.PROCESS[config.INITIAL]['model']
        serialized_data = serializer(data=request.POST)
        record_added = False
        if serialized_data.is_valid():
            process_request = model.objects.get(pk=pk)
            action = serialized_data.validated_data['status']
            role = get_role(config, action, process_request.role)
            # final = is_final(config, process_request.role)
            update_process(process_request, role[0], role[2])
            serialized_data.save_as(role[1], request, pk)
            record_added = True
        modal = config.PROCESS[config.INITIAL]['model']
        display_fields = config.DETAIL
        fields = [f.name for f in modal._meta.get_fields()]
        fields = filter(lambda x: x in display_fields, fields)
        fields.sort(reverse=True)
        process_detail = self.get_process_detail(request, **kwargs)
        object_detail = self.get_object_detail(request, pk, **kwargs)
        process_status_detail = self.process_status_detail(request, pk, **kwargs)
        return Response({'serializer': serializer,
                         'pk': pk,
                         'process_detail': process_detail,
                         'object_detail': object_detail,
                         'process_status_detail': process_status_detail[0],
                         'current_role': process_status_detail[1],
                         'app_name': app_name,
                         'record_added':record_added})

    def delete(self, request, pk, **kwargs):
        activity = self.get_object(request, pk, **kwargs)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApproveListView(APIView):
    renderer_classes = (TemplateHTMLRenderer,)
    template_name = 'templates/process_form.html'

    def get(self, request, **kwargs):
        app_name = get_app_name(request, **kwargs)
        config = get_app_detail(request, **kwargs)
        transition = config.PROCESS[config.INITIAL]['transitions']
        serializer = config.PROCESS[transition[0]]['serializer']
        modal = config.PROCESS[config.INITIAL]['model']
        transaction_modal = config.PROCESS[transition[0]]['model'].__name__.lower()
        queryset = manager_queryset(request, **kwargs)
        fields = get_process_transactions(modal, transaction_modal, config.DETAIL, "approval")
        serializer = serializer()
        return Response({'queryset': queryset, 'serializer': serializer, 'fields': fields, 'app_name': app_name})










