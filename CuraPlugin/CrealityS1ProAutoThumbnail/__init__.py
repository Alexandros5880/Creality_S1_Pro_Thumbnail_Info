from .CrealityS1ProAutoThumbnailPlugin import CrealityS1ProAutoThumbnailPlugin

def getMetaData():
    return {}

def register(app):
    return {"extension": CrealityS1ProAutoThumbnailPlugin()}
