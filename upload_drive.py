from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# 서비스 계정 키 파일 경로
SERVICE_ACCOUNT_FILE = 'service_account.json'

# Google Drive API 인증 (서비스 계정)
def authenticate_google_drive():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=credentials)


# Google Drive 공유 폴더 ID
FOLDER_ID = '1GwbcEfpaCbcbkhBpXjR4GOO6UFVjceiz'

# 파일 업로드 함수
def upload_to_drive(service, file_name, file_data, mime_type):
    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID]
    }
    media = MediaIoBaseUpload(io.BytesIO(file_data), mimetype=mime_type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded {file_name} to shared folder with ID: {file.get('id')}")
