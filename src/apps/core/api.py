from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.core.tasks import export_to_aha


@api_view(['POST'])
def export_group(request):

    export.delay(request.data, request.user.id)
    return Response({"status": "ok"})
