from enum import Enum
from photoDB import PhotoDB

class PhotoState(Enum):
    UPLOADING = 1
    UPLOADED = 2
    NOT_TAGGED = 3
    TAGGED = 4


print(PhotoState.TAGGED.name)