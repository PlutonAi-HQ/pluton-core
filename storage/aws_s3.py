import boto3
from botocore.exceptions import ClientError
import logging
from typing import Union, BinaryIO
import os
from dotenv import load_dotenv

load_dotenv()


class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "ap-southeast-1"),
        )
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")

    def upload_file(
        self, file_obj: Union[str, BinaryIO], object_name: str, content_type: str = None
    ) -> dict:
        """
        Upload file lên S3 bucket

        Args:
            file_obj: Có thể là đường dẫn file hoặc file object
            object_name: Tên file trên S3
            content_type: MIME type của file

        Returns:
            dict: Thông tin upload status và URL của file
        """
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            # Nếu file_obj là string, coi như đường dẫn file
            if isinstance(file_obj, str):
                self.s3_client.upload_file(
                    file_obj, self.bucket_name, object_name, ExtraArgs=extra_args
                )
            else:
                # Nếu là file object
                self.s3_client.upload_fileobj(
                    file_obj, self.bucket_name, object_name, ExtraArgs=extra_args
                )

            # Tạo URL của file
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{object_name}"

            return {
                "status": "success",
                "message": "File uploaded successfully",
                "url": url,
            }

        except ClientError as e:
            logging.error(e)
            return {"status": "error", "message": str(e)}
