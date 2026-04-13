from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.user.serializers import LoginSerializer, RegisterSerializer, UserProfileSerializer, UserUpdateSerializer
from app.user.services import login, logout, token_refresh


class RegisterView(APIView):
    @extend_schema(
        summary="회원가입",
        description="이메일, 닉네임, 비밀번호로 회원가입",
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(description="회원가입 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입 완료되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @extend_schema(
        summary="로그인",
        description="이메일&비밀번호로 로그인. 쿠키에 JWT 토큰 저장",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="로그인 성공"),
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="이메일 또는 비밀번호 불일치"),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tokens = login(serializer.validated_data["email"], serializer.validated_data["password"])
        if tokens is None:
            return Response(
                {"message": "이메일 또는 비밀번호가 올바르지 않습니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response({"message": "로그인 되었습니다"}, status=status.HTTP_200_OK)
        response.set_cookie(
            "access_token",
            tokens["access_token"],
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=60 * 30,
        )
        response.set_cookie(
            "refresh_token",
            tokens["refresh_token"],
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=60 * 60 * 24,
        )
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="로그아웃",
        description="Refresh Token 블랙리스트 추가 및 쿠키 삭제",
        responses={
            200: OpenApiResponse(description="로그아웃 성공"),
            401: OpenApiResponse(description="인증 필요"),
        },
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not logout(refresh_token):
            return Response({"message": "Refresh Token이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({"message": "로그아웃 되었습니다"}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class TokenRefreshView(APIView):
    @extend_schema(
        summary="토큰 재발급",
        description="쿠키의 Refresh Token으로 새 Access Token발급",
        responses={
            200: OpenApiResponse(description="토큰 재발급 성공"),
            401: OpenApiResponse(description="Refresh Token 없음"),
        },
    )
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        token = token_refresh(refresh_token)
        if token is None:
            return Response({"message": "Refresh Token이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({"message": "토큰 재발급 성공"}, status=status.HTTP_200_OK)
        response.set_cookie(
            "access_token",
            token["access_token"],
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=60 * 30,
        )
        return response


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="프로필 조회",
        description="로그인한 유저의 프로필 조회",
        responses={
            200: UserProfileSerializer,
            401: OpenApiResponse(description="인증 필요"),
        },
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="프로필 수정",
        description="닉네임, 성별, 나이, 직업 수정 가능. 변경할 필드만 보내면 됨",
        request=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer,
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 필요"),
        },
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="회원 탈퇴",
        description="소프트 딜리트 방식으로 탈퇴처리",
        responses={
            204: OpenApiResponse(description="탈퇴 성공"),
            401: OpenApiResponse(description="인증 필요"),
        },
    )
    def delete(self, request):
        request.user.is_delete = True
        request.user.save()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
