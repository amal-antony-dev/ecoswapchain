from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import RootCategorySerializer, MainCategorySerializer
from esc_product.models import RootCategory, MainCategory

class CategoryRetrieveView(APIView):
    def get(self, request):
        # Query all RootCategory and MainCategory data
        root_categories = RootCategory.objects.all()
        main_categories = MainCategory.objects.all()

        # Serialize the data
        root_data = RootCategorySerializer(root_categories, many=True).data
        main_data = MainCategorySerializer(main_categories, many=True).data

        # Return serialized data in response
        return Response({
            "root": root_data,
            "main": main_data
        }, status=200)
