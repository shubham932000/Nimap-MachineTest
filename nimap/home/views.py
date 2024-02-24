from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Client, Project 
from .serializers import ClientSerializer, ProjectSerializer
from django.utils import timezone



class ClientListCreateAPIView(APIView):
    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response({'status': 200, 'data': serializer.data})

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 201, 'data': serializer.data, 'message': 'Client created successfully'})
        return Response({'status': 400, 'errors': serializer.errors, 'message': 'Failed to create client'})

class ClientRetrieveUpdateDestroyAPIView(APIView):
    def get(self, request, id):
        client = Client.objects.filter(id=id).first()
        if not client:
            return Response({'status': 404, 'message': 'Client not found'})
        
        client_data = ClientSerializer(client).data
        projects_data = [
            {'id': project['id'], 'project_name': project['project_name']} 
            for project in client.projects.values('id', 'project_name')
        ]
        
        response_data = {
            "id": client_data['id'],
            "client_name": client_data['client_name'],
            "projects": projects_data,
            "created_by": client_data['created_by']
        }

        return Response({'status': 200, 'data': response_data})

    def get_object(self, id):
        try:
            return Client.objects.get(id=id)
        except Client.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def patch(self, request, id):
        client = self.get_object(id)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_at=timezone.now())
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        client = self.get_object(id)
        serializer = ClientSerializer(client, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_at=timezone.now())
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        client = Client.objects.filter(id=id).first()
        if not client:
            return Response({'status': 404, 'message': 'Client not found'})

        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProjectCreateAPIView(APIView):
    def post(self, request, id):
        
        client = Client.objects.filter(id=id).first()
        if not client:
            return Response({'message': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

        
        created_at = timezone.now()

        
        if request.user.is_authenticated:
            created_by = request.user.username
        else:
            created_by = 'Anonymous'

        
        project_data = {
            'project_name': request.data.get('project_name'),
            'client': id,  
            'created_at': created_at,
            'created_by': created_by
        }
        serializer = ProjectSerializer(data=project_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        project = serializer.save()

        users_data = request.data.get('users', [])
        for user_data in users_data:
            user_id = user_data.get('id')
            user = User.objects.filter(id=user_id).first()
            if user:
                project.users.add(user)

        serialized_project = ProjectSerializer(project)

        return Response(serialized_project.data, status=status.HTTP_201_CREATED)

class ProjectListAPIView(APIView):
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
