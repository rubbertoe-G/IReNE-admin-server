"""
documents.py
====================================
Every route regarding documents, including publishing or unpublishing a document and seeing all of current documents in the systen can be found here.
"""
from flask import Blueprint, request, current_app
from utils.responses import ApiResult, ApiException
from exceptions.handler import AdminServerApiError, AdminServerAuthError
from flask_jwt_extended import get_jwt_identity, fresh_jwt_required
from daos.documents_dao import DocumentsDAO
from daos.collaborators_dao import CollaboratorsDAO
from utils.validators import objectId_is_valid
import json

blueprint = Blueprint('documents', __name__, url_prefix='/admin/documents')
dao = DocumentsDAO()
daoCollab = CollaboratorsDAO()


@blueprint.route('/', methods=['GET'])
@fresh_jwt_required
def documents():
    """
    Retrieve a list of all the documents in the database.
    Returns
    -------
    Document[]
        List of collaborators currently in the system.
    """
    documents = dao.get_all_documents()
    print(json.loads(documents))
    return ApiResult(
        body={'documents': json.loads(documents)}
    )


@blueprint.route('/view/<docID>', methods=['GET'])
@fresh_jwt_required
def documents_view(docID):
    """
    Retrieve a list of metadata of all the documents in the database.
    """

    document = dao.get_document(docID)
    if not document:
        raise AdminServerApiError(
            msg='The documents ID given was not found.',
            status=404
        )
    collab = document.creatoriD
    actors = []
    authors = []
    sections = []
    for author in document.author:
        authors.append(json.loads(author.to_json()))
    for actor in document.actor:
        actors.append(json.loads(actor.to_json()))
    for section in document.section:
        sections.append(json.loads(section.to_json()))
    body = {
        '_id': str(document.id),
        'title': document.title,
        'description': document.description,
        'creatorFullName': collab.first_name + " " + collab.last_name,
        'creatorEmail': collab.email,
        'creationDate': document.creationDate,
        'lastModificationDate': document.lastModificationDate,
        'incidentDate': document.incidentDate,
        'tagsDoc': document.tagsDoc,
        'infrasDocList': document.infrasDocList,
        'damageDocList': document.damageDocList,
        'author': authors,
        'actor': actors,
        'section': sections
    }
    body = json.dumps(body)
    return ApiResult(body=
                     {'document': json.loads(body)}
                     )


@blueprint.route('/publish', methods=['PUT'])
@fresh_jwt_required
def documents_publish():
    """
    Pusblish a document. 
    
    Parameters
    ----------
    docID : ObjectId
        12-byte MongoDB compliant Object id of the document to be publish.
    
    Returns
    -------
    Document
        Document that has been published.
    
    Raises
    ------
    AdminServerApiError
        If the document id is not valid or if a document with the given id was not found.

    """
    doc_id = request.form.get('docID')
    valid_doc_id = objectId_is_valid(doc_id)
    if not valid_doc_id:
        raise AdminServerApiError(
            msg='The documents ID given is not valid.',
            status=400
        )
    document = dao.publish_document(doc_id)
    if not document:
        raise AdminServerApiError(
            msg='The documents ID given was not found.',
            status=404
        )
    return ApiResult(body={'docID': doc_id})


@blueprint.route('/unpublish', methods=['PUT'])
@fresh_jwt_required
def documents_unpublish():
    """
    Unpusblish a document. 
    
    Parameters
    ----------
    docID : ObjectId
        12-byte MongoDB compliant Object id of the document to be unpublish.
    
    Returns
    -------
    Document
        Document that has been unpublished.
    
    Raises
    ------
    AdminServerApiError
        If the document id is not valid or if a document with the given id was not found.

    """
    doc_id = request.form.get('docID')
    valid_doc_id = objectId_is_valid(doc_id)
    if not valid_doc_id:
        raise AdminServerApiError(
            msg='The documents ID given is not valid.',
            status=400
        )
    doc = dao.unpublish_document(doc_id)
    if not doc:
        raise AdminServerApiError(
            msg='The documents ID given was not found.',
            status=404
        )
    return ApiResult(body=
                     {'docID': doc_id}
                     )


@blueprint.before_app_request
def verify_identity():
    if current_app.config['ADMIN_IDENTITY']:
       raise AdminServerAuthError('AuthError', msg='Another administrator is already performing operations')
