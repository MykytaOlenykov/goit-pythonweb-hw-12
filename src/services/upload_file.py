import cloudinary
import cloudinary.uploader
from fastapi import UploadFile


class UploadFileService:
    """
    UploadFileService is responsible for handling file uploads to Cloudinary.

    Args:
        - cloud_name: str - The name of the Cloudinary cloud.
        - api_key: str - The API key for Cloudinary.
        - api_secret: str - The API secret for Cloudinary.

    Methods:
        - upload_file: Uploads a file to Cloudinary and returns the URL.
    """

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file: UploadFile, user_id: int) -> str:
        """
        Uploads a file to Cloudinary and generates a URL for the uploaded file.

        Args:
            - file: UploadFile - The file to be uploaded.
            - user_id: int - The ID of the user associated with the uploaded file.

        Returns:
            - str - The URL of the uploaded file.
        """

        public_id = f"ContactsApp/{user_id}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
