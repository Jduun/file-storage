from . import test_files, ROOT_FOLDER, other_dir
from http import HTTPStatus
from io import BytesIO
import json
from datetime import datetime, timedelta
from db.postgres import File
import random
from services import FileStorageService
import os
import uuid


def test_get_files(client):
    response = client.get("/files")
    assert response.json == [test_file.to_dict() for test_file in test_files]
    assert response.status_code == HTTPStatus.OK


def test_get_files_in_folder(client):
    response = client.get(f"/files?path_to_folder={other_dir}")
    search_pattern = other_dir
    if not search_pattern.endswith("/"):
        search_pattern += "/"
    assert response.json == [
        test_file.to_dict()
        for test_file in test_files
        if test_file.filepath.startswith(search_pattern)
    ]
    assert response.status_code == HTTPStatus.OK


def test_upload_file(client):
    filename = "new_test_file"
    extension = ".txt"
    filepath = "/"
    comment = "This is new test file!"
    created_at = datetime.utcnow().isoformat()
    with open(filename + extension, "w"):
        pass
    response = client.post(
        "/files",
        data={
            "file": (BytesIO(b""), filename + extension),
            "json": json.dumps({"filepath": filepath, "comment": comment}),
        },
    )
    data = response.json
    assert abs(
        datetime.fromisoformat(created_at) - datetime.fromisoformat(data["created_at"])
    ) <= timedelta(minutes=1)
    created_at = datetime.fromisoformat(data["created_at"])
    uploaded_file = File(
        id=data["id"],
        filename=filename,
        extension=extension,
        size=0,
        filepath=filepath,
        created_at=created_at,
        modified_at=None,
        comment=comment,
    )
    assert uploaded_file.to_dict() == data
    assert response.status_code == HTTPStatus.CREATED
    test_files.append(uploaded_file)


def test_delete_file(client):
    file_to_delete = random.choice(test_files)
    response = client.delete(f"/files/{file_to_delete.id}")
    data = response.json
    assert file_to_delete.to_dict() == data
    assert response.status_code == HTTPStatus.OK
    test_files.remove(file_to_delete)


def test_update_file(client):
    file_to_update = random.choice(test_files)
    new_comment = "Updated comment!"
    new_filepath = "/new_folder/"
    new_filename = "new_filename"
    file_to_update.comment = new_comment
    file_to_update.filename = new_filename
    file_to_update.filepath = new_filepath
    file_to_update.modified_at = datetime.utcnow()
    response = client.put(
        f"/files/{file_to_update.id}",
        json={
            "comment": new_comment,
            "filepath": new_filepath,
            "filename": new_filename,
        },
    )
    data = response.json
    assert abs(
        datetime.fromisoformat(file_to_update.to_dict()["modified_at"])
        - datetime.fromisoformat(data["modified_at"])
    ) <= timedelta(minutes=1)
    file_to_update.modified_at = datetime.fromisoformat(data["modified_at"])
    assert file_to_update.to_dict() == data
    assert response.status_code == HTTPStatus.OK


def test_download_file(client):
    file_to_download = random.choice(test_files)
    response = client.get(f"/files/{file_to_download.id}/download")
    content_disposition = response.headers.get("content-disposition")
    assert response.status_code == HTTPStatus.OK
    assert content_disposition is not None
    assert (
        f"attachment; filename={file_to_download.filename + file_to_download.extension}"
        in content_disposition
    )


def test_sync_file(client):
    num_files_to_delete = len(test_files) // 3
    num_files_to_add = num_files_to_delete

    files_to_delete = random.sample(test_files, num_files_to_delete)
    for file_to_delete in files_to_delete:
        os.remove(FileStorageService.get_abs_path(file_to_delete))

    files_to_add = [
        File(
            id=str(uuid.uuid4()),
            filename=f"TEST{i}",
            extension=".pdf",
            size=0,
            filepath="/some_folder/",
            created_at=datetime.utcnow(),
            modified_at=None,
            comment=f"This is TEST file {i}",
        )
        for i in range(num_files_to_add)
    ]
    for file_to_add in files_to_add:
        path_to_folder = ROOT_FOLDER + file_to_add.filepath
        os.makedirs(path_to_folder, exist_ok=True)
        with open(FileStorageService.get_abs_path(file_to_add), "w"):
            pass

    response = client.post(f"/files/sync")
    assert response.status_code == HTTPStatus.OK
    data = response.json
    assert data["files_to_add"] == [
        FileStorageService.get_rel_path(file) for file in files_to_add
    ]
    assert data["files_to_delete"] == [
        FileStorageService.get_rel_path(file) for file in files_to_delete
    ]
