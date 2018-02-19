import os
import requests
import zipfile
import boto3
import mimetypes

import gzip
import shutil

from datetime import datetime
from datetime import timedelta

types_to_convert = ['html', 'css', 'js']
def lambda_handler(event, context):
    # TODO implement
    git_url = os.environ['GIT_URL']
    folder_name = os.environ['FOLDER_NAME']
    bucket_name = os.environ['BUCKET_NAME']
    zip_location = '/tmp/repo.zip'
    
    # source directory
    source_dir = '/tmp/repo/'+folder_name
    # destination directory name (on s3)
    dest_dir = ''

    response = requests.get(git_url)
    with open(zip_location, 'wb') as f:
        f.write(response.content)
    
    zip_ref = zipfile.ZipFile(zip_location, 'r')
    zip_ref.extractall('/tmp/repo')
    zip_ref.close()
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()
    
    uploadFiles = {}

    for folder, subs, files in os.walk(source_dir):
        for filename in files:
            filepath = os.path.join(folder, filename)
            uploadFiles[filename] = filepath

    for filename in uploadFiles:
        sourcepath = uploadFiles[filename]
        destpath = sourcepath[len(source_dir)+1:]
        
        has_been_compressed = False
        file_mimetype = get_mime_type(filename)

        if(should_be_compressed(sourcepath)):
            compress_file(sourcepath)
            has_been_compressed = True

        args = get_extra_args(file_mimetype, has_been_compressed)
        print 'Uploading %s to Amazon S3 bucket %s to %s' % \
               (sourcepath, bucket_name, destpath)
        bucket.upload_file(sourcepath, destpath, ExtraArgs=args)
        

    return 'Update complete'

def should_be_compressed(sourcepath):
    tokens = sourcepath.split('.')
    filetype = tokens[len(tokens)-1]
    if filetype in types_to_convert:
        return True

    return False

def compress_file(sourcepath):
    gz_name = sourcepath+'.gz'
    with open(sourcepath, 'rb') as f_in, gzip.open(gz_name, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    os.system('rm ' + sourcepath)
    os.system('mv ' + gz_name + ' ' + sourcepath)

def get_extra_args(file_mimetype, has_been_compressed):
    args = {}

    if(file_mimetype is not None):
        args['ContentType'] = file_mimetype

    if(has_been_compressed):
        args['ContentEncoding'] = 'gzip'

    # one day
    args['CacheControl'] = '86400' 

    # 30 days
    expire_datetime = datetime.now() + timedelta(30)

    args['Expires'] = expire_datetime

    return args


def get_mime_type(filename):
    mime = mimetypes.guess_type(filename)
    return mime[0]