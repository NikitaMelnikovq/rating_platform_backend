from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .permissions import IsAdminUser, IsTeacherUser
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"message": "Hello, Admin!"})

class TeacherOnlyView(APIView):
    permission_classes = [IsTeacherUser]

    def get(self, request):
        return Response({"message": "Hello, Teacher!"})
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    serializer = UserSerializer(request.user, context={'request': request})  # Added context
    return Response(serializer.data)