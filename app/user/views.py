from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView

from app.user.serializers import LoginSerializer, RegisterSerializer, UserUpdateSerializer
from app.user.services import login, logout, token_refresh


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입 완료되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        tokens = login(serializer.validated_data["email"], serializer.validated_data["password"])
        if tokens is None:
            return Response(
                {"message": "이메일 또는 비밀번호가 올바르지 않습니다."},
            )

        response = Response({"message": "로그인 되었습니다"}, status=HTTP_200_OK)
        response.set_cookie("access_token", tokens["access_token"], httponly=True)
        response.set_cookie("refresh_token", tokens["refresh_token"], httponly=True)
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        logout(refresh_token)

        response = Response({"message": "로그아웃 되었습니다"}, status=HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        token = token_refresh(refresh_token)
        if token is None:
            return Response({"message": "Refresh Token이 없습니다."}, status=HTTP_401_UNAUTHORIZED)

        response = Response({"message": "토큰 재발급 성공"}, status=HTTP_200_OK)
        response.set_cookie("access_token", token["access_token"], httponly=True)
        return response


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserUpdateSerializer(request.user)
        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request):
        request.user.is_delete = True
        request.user.save()
        return Response({"message": "Deleted successfully"}, status=HTTP_204_NO_CONTENT)
