from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .service import ask, create_thread
from django.shortcuts import get_object_or_404
from .models import Dog, Reservation
from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter


class matchingAIAPIView(APIView):

    def post(self, request):
        assistant_id = "asst_lBiCsFZlIKMddvjyIOJ4A4Ix"
        user_message = request.data.get('text')
        thread_id = request.data.get('thread_id')

        if not user_message:
            return Response({"error": "Empty message"}, status=status.HTTP_400_BAD_REQUEST)

        # 쓰레드 ID가 없으면 새로운 쓰레드 생성
        if not thread_id:
            thread_id = create_thread()
            if not thread_id:
                return Response({"error": "Failed to create a new thread"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 서비스 호출
        response = ask(thread_id=thread_id, assistant_id=assistant_id, user_message=user_message)

        if "error" in response:
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 응답 데이터에서 추천된 유기견들의 정보를 채워 넣기
        recommendations = response.get("recommendations", [])

        enriched_recommendations = []
        for rec in recommendations:
            dog_id = rec.get("dog_id")
            if dog_id:
                # 유기견 정보를 데이터베이스에서 가져오기
                dog = get_object_or_404(Dog, dog_id=dog_id)

                enriched_recommendations.append({
                    "dog_id": dog.dog_id,
                    "name": dog.name,
                    "age": dog.age,
                    "gender": dog.gender,
                    "match_score": rec.get("match_score"),
                    "dog_image_url": dog.photo.url,
                    "reason": rec.get("reason")
                })

        # ai_text에 마침표 뒤에 줄바꿈 추가
        ai_text = response.get("ai_text", "")
        if ai_text:
            ai_text = ai_text.replace(".", ".\n")

        # 응답 구성
        response_data = {
            "ai_text": ai_text,
            "tags": response.get("tags"),
            "recommendations": enriched_recommendations
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def get(self, request):
        # 쿼리스트링 파라미터 받기
        dog_id = request.query_params.get('dog_id')
        name = request.query_params.get('name')
        age = request.query_params.get('age')
        gender = request.query_params.get('gender')
        tags = request.query_params.get('tags')

        # 필터링 조건 생성
        filters = {}
        if dog_id:
            filters['dog_id'] = dog_id  # 특정 dog_id로 필터링
        if name:
            filters['name__icontains'] = name  # 이름에 해당 문자열이 포함된 경우
        if age:
            filters['age'] = age  # 정확히 해당 나이
        if gender:
            filters['gender'] = gender  # 정확히 해당 성별
        if tags:
            filters['tags__icontains'] = tags  # 태그에 해당 문자열이 포함된 경우

        # 필터링된 Dog 객체 가져오기 (단일 객체)
        dog = get_object_or_404(Dog, **filters)

        # 데이터 직렬화
        dog_data = {
            "dog_id": dog.dog_id,
            "name": dog.name,
            "age": dog.age,
            "gender": dog.gender,
            "tags": dog.tags_list,  # 태그 리스트로 변환
            "remaining_days": dog.remaining_days,
            "description": dog.description,
            "shelter": {
                "shelter_id": dog.shelter.id,
                "name": dog.shelter.name,
                "description": dog.shelter.description,
                "contact": dog.shelter.contact,
                "shelter_image_url": dog.shelter.photo.url if dog.shelter.photo else None
            },
            "registration_number": dog.registration_number,
            "owner": dog.owner,
            "dog_image_url": dog.photo.url if dog.photo else None
        }

        # 응답 반환
        return Response(dog_data, status=status.HTTP_200_OK)


class CompleteReservationAPIView(APIView):

    def post(self, request):
        # 입력 데이터 받기
        reservation_period = request.data.get('date')
        dog_id = request.data.get('dog_id')
        guest_name = request.data.get('guest_name', 'guest')  # 사용자 이름, 없으면 기본값 "guest"

        # 필수 입력 데이터 확인
        if not reservation_period or not dog_id:
            return Response({"error": "Invalid input data"}, status=status.HTTP_400_BAD_REQUEST)

        # 유기견 객체 가져오기
        dog = get_object_or_404(Dog, dog_id=dog_id)

        # 예약 기간 파싱
        try:
            start_str, end_str = reservation_period.split("~")
            start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        # 예약 내역 생성
        reservation = Reservation.objects.create(
            dog=dog,
            start_date=start_date,
            end_date=end_date,
            guest_name=guest_name
        )

        # 응답 데이터 구성
        response_data = {
            "reservation_id": reservation.id,
            "reservation_number": reservation.reservation_number,
            "dog_id": reservation.dog.dog_id,
            "dog_image_url": reservation.dog.photo.url,
            "dog_name": reservation.dog.name,
            "shelter_id": reservation.dog.shelter.id,
            "shelter_image_url": reservation.dog.shelter.photo.url,
            "shelter_name": reservation.dog.shelter.name,
            "shelter_contact": reservation.dog.shelter.contact,
            "start_date": reservation.start_date,
            "end_date": reservation.end_date,
            "guest_name": reservation.guest_name,
            "created_at": reservation.created_at
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


    def get(self, request):
        reservation_number = request.query_params.get('reservation_number')

        # 예약 번호로 예약 객체 가져오기
        reservation = get_object_or_404(Reservation, reservation_number=reservation_number)

        response_data = {
            "reservation_id": reservation.id,
            "reservation_number": reservation.reservation_number,
            "dog_id": reservation.dog.dog_id,
            "dog_image_url": reservation.dog.photo.url,
            "dog_name": reservation.dog.name,
            "shelter_id": reservation.dog.shelter.id,
            "shelter_image_url": reservation.dog.shelter.photo.url,
            "shelter_name": reservation.dog.shelter.name,
            "shelter_contact": reservation.dog.shelter.contact,
            "start_date": reservation.start_date,
            "end_date": reservation.end_date,
            "guest_name": reservation.guest_name,
            "created_at": reservation.created_at
        }

        return Response(response_data, status=status.HTTP_200_OK)


class FindDogAPIView(APIView):

    def get(self, request):
        # 쿼리스트링 파라미터 받기
        registration_number = request.query_params.get('registration_number')
        owner = request.query_params.get('owner')

        # Dog 객체를 필터링하여 가져오기
        dog = get_object_or_404(Dog, registration_number=registration_number, owner=owner)

        # Dog와 연결된 Shelter 정보 포함하여 응답 데이터 생성
        response = {
            "dog": {
                "dog_id": dog.dog_id,
                "name": dog.name,
                "age": dog.age,
                "gender": dog.gender,
                "tags": dog.tags_list,  # 태그 리스트로 변환
                "remaining_days": dog.remaining_days,
                "description": dog.description,
                "registration_number": dog.registration_number,
                "owner": dog.owner,
                "dog_image_url": dog.photo.url if dog.photo else None
            },
            "shelter": {
                "shelter_id": dog.shelter.id,
                "name": dog.shelter.name,
                "description": dog.shelter.description,
                "contact": dog.shelter.contact,
                "shelter_image_url": dog.shelter.photo.url if dog.shelter.photo else None
            }
        }

        return Response(response, status=status.HTTP_200_OK)



