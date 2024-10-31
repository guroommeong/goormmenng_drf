# 베이스 이미지 설정
FROM python:3.12-slim

# 작업 디렉터리 생성 및 이동
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . /app/

# Django 관리 명령어 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
