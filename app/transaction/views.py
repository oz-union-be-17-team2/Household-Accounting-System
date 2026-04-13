from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .selectors import get_transaction_list
from .serializers import TransactionSerializer


# 현재 접근 권한을 get_queryset으로 막은 이유는 필터에서 본인 데이터만 조회하게 했기 때문에
# 타인 접근시 404로 반환되서 "데이터가 없다"의 의미로 보안상 더 좋다.
# 만약 permission_classes에서 막는다면 403으로 반환되서 "권한이 없다"의 의미로
# 데이터 존재여부를 알려줄 수 있게 된다.
class TransactionListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    # class ListCreateAPIView(mixins.ListModelMixin,
    #                         mixins.CreateModelMixin,
    #                         GenericAPIView):
    #     """
    #     Concrete view for listing a queryset or creating a model instance.
    #     """
    #     def get(self, request, *args, **kwargs):
    #         return self.list(request, *args, **kwargs)
    #
    #     def post(self, request, *args, **kwargs):
    #         return self.create(request, *args, **kwargs)
    # ListCreateAPIView에서는 get_queryset을 오버라이드 하기 때문에 queryset =을 지정하지 하지 않는다.
    # 이유는 필터링 로직이 있어서 get_queryset을 오버라이드 한거라서 사용함
    # CreateModelMixin에서 serializer = self.get.serializer(data=request.data)으로 JSON형태를 python형태로 변환하고
    # serializer.is_valid(raise_exception=True)를 통해서 유효성 검사를 진행
    @extend_schema(
        summary="거래내역 목록 조회",
        description="로그인한 유저의 거래내역 목록을 조회합니다.",
        parameters=[
            OpenApiParameter(name="type", description="거래 유형 (DEPOSIT/WITHDRAWAL)"),
            OpenApiParameter(name="amount_min", description="최소 금액"),
            OpenApiParameter(name="amount_max", description="최대 금액"),
        ],
        responses={200: TransactionSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="거래내역 생성",
        description="새로운 거래내역을 생성합니다.",
        request=TransactionSerializer,
        responses={201: TransactionSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return get_transaction_list(
            user=self.request.user,
            transaction_type=self.request.query_params.get("type"),
            amount_min=self.request.query_params.get("amount_min"),
            amount_max=self.request.query_params.get("amount_max"),
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # user는 read_only로 설정해 두었기에 클라이언트가 전달하지 못함
        # 그래서 저장 시점에 request.user를 직접 주입하기 위해서 perform_create()를 오버라이드 한 것입니다


class TransactionDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    @extend_schema(
        summary="거래내역 단건 조회",
        description="특정 거래내역을 조회합니다.",
        responses={200: TransactionSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="거래내역 수정",
        description="특정 거래내역을 전체 수정합니다.",
        request=TransactionSerializer,
        responses={200: TransactionSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="거래내역 부분 수정",
        description="특정 거래내역을 부분 수정합니다.",
        request=TransactionSerializer,
        responses={200: TransactionSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="거래내역 삭제",
        description="특정 거래내역을 삭제합니다.",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return get_transaction_list(user=self.request.user)
