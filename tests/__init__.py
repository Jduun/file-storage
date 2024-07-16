from _datetime import datetime
from db.postgres import File
import uuid
import os
import random

ROOT_FOLDER = os.getenv("ROOT_FOLDER")
NUM_FIlES = 5
other_dir = "/FOLDER/"

test_files = [
    File(
        id=str(uuid.uuid4()),
        filename=f"test{i}",
        extension=".txt",
        size=i * 100,
        filepath="/",
        created_at=datetime.utcnow(),
        modified_at=None,
        comment=f"this is test file {i}",
    )
    for i in range(NUM_FIlES)
]
num_files_to_move = len(test_files) // 2
files_to_move = random.sample(test_files, num_files_to_move)
for file in files_to_move:
    file.filepath = "/FOLDER/"
