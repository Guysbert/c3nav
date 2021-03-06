from collections import OrderedDict

from django.core import signing
from django.core.signing import BadSignature
from django.http import Http404
from rest_framework.decorators import detail_route
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from c3nav.editor.hosters import get_hoster_for_package, hosters
from c3nav.editor.serializers import HosterSerializer, TaskSerializer
from c3nav.editor.tasks import submit_edit_task
from c3nav.mapdata.models.package import Package


class HosterViewSet(ViewSet):
    """
    Retrieve and interact with package hosters
    """
    lookup_field = 'name'

    def retrieve(self, request, name=None):
        if name not in hosters:
            raise Http404
        serializer = HosterSerializer(hosters[name], context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def state(self, request, name=None):
        if name not in hosters:
            raise Http404

        hoster = hosters[name]
        state = hoster.get_state(request)
        error = hoster.get_error(request) if state == 'logged_out' else None

        return Response(OrderedDict((
            ('state', state),
            ('error', error),
        )))

    @detail_route(methods=['post'])
    def auth_uri(self, request, name=None):
        if name not in hosters:
            raise Http404
        return Response({
            'auth_uri': hosters[name].get_auth_uri(request)
        })

    @detail_route(methods=['post'])
    def submit(self, request, name=None):
        if name not in hosters:
            raise Http404
        hoster = hosters[name]

        if 'data' not in request.POST:
            raise ValidationError('Missing POST parameter: data')

        if 'commit_msg' not in request.POST:
            raise ValidationError('Missing POST parameter: commit_msg')

        data = request.POST['data']
        commit_msg = request.POST['commit_msg'].strip()

        if not commit_msg:
            raise ValidationError('POST parameter may not be empty: commit_msg')

        try:
            data = signing.loads(data)
        except BadSignature:
            raise ValidationError('Bad data signature.')

        if data['type'] != 'editor.edit':
            raise ValidationError('Wrong data type.')

        package = Package.objects.filter(name=data['package_name']).first()
        data_hoster = None
        if package is not None:
            data_hoster = get_hoster_for_package(package)

        if hoster != data_hoster:
            raise ValidationError('Wrong hoster.')

        data['commit_msg'] = commit_msg

        task = hoster.submit_edit(request, data)

        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)


class SubmitTaskViewSet(ViewSet):
    """
    Get hoster submit tasks
    """
    lookup_field = 'id_'

    def retrieve(self, request, id_=None):
        task = submit_edit_task.AsyncResult(task_id=id_)
        try:
            task.ready()
        except:
            raise Http404

        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)
