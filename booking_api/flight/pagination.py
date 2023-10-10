from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status


class CombinedPagination(PageNumberPagination):

    # def paginate_queryset(self, queryset, request, view=None):
    #     self.page_size = int(request.GET.get('page_size', self.page_size))
        
    #     page = self.get_page_number(request)
    #     if page == 1:
    #         return self.paginator_class(queryset[:self.page_size], self.page_size)
    #     else:
    #         return self.paginator_class(queryset, self.page_size)
    

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            'next': self.get_next_link(),
            "previous": self.get_previous_link(),
            "result": data
        }, status=status.HTTP_200_OK)

class FlightCombinedPagination(PageNumberPagination):
    # paginator_class = PageNumberPagination

    # def paginate_queryset(self, queryset, request, view=None):
    #     self.page_size = int(request.GET.get('page_size', self.page_size))
    #     page = request.GET.get('page', 1)
    #     try:
    #         page = int(page)
    #     except ValueError:
    #         page = 1
    #     return self.paginator_class(queryset, self.page_size).page(page)
    
    # def get_page_number(self, request):
    #     page = request.GET.get('page', 1)
    #     try:
    #         page = int(page)
    #     except ValueError:
    #         page = 1
    #     return max(1, page)

    def get_paginated_response(self, data):
        count = data.pop('count')
        return Response({
            "count":count,
            'next': self.get_next_link(),
            "previous": self.get_previous_link(),
            "result": data
        }, status=status.HTTP_200_OK)