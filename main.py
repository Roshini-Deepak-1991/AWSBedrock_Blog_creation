import json
import boto3
import botocore.config
from datetime import datetime

# First usecase generate content

# AWS bedrock call##

def content_generation(blogtopic:str)->str:
    prompt = f""" write a 200 word blog post on {blogtopic}"""
    body = {
        "prompt" : prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p" : 0.9

    }

    try:
        # Invoke the model with the request.
        bedrock = boto3.client(
            service_name= "bedrock-runtime"
            region_name = "us-east-1"
            config=botocore.config.Config(read_timeout = 300, retries = {'max_attempts' : 3})
        )
        response = bedrock.invoke_model(body = json.dumps(body) , modelId = "us.meta.llama4-scout-17b-instruct-v1:0")
        response_content = response.get("body").read()
        response_data = json.loads(response_content)
        #print(response_data)
        blog_details = response_data["generation"]
        return blog_details

    except Exception as e:
        print(e)
        return ""



# S3 uploaader function

def s3_uploader(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Body = generate_blog , Bucket = s3_bucket, Key= s3_key)
        print(f'File uploasded succesfully {s3_bucket}')
    except Exception as e:
        print(f'Error Uploading the file: {e}')

# My main lambda function (Here calling the s3 uploader function)

import json

def lambda_handler(event, context):
    event = json.loads(event['body'])
    blog_topic = event['blogTopic']

    generate_blog = content_generation(blogtopic=blog_topic)


    if generate_blog:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M_%S")
        s3_key = f"blogs/{current_time}.txt"
        s3_bucket = "learningbedrock"
        s3_uploader(s3_key=s3_key, s3_bucket=s3_bucket,generate_blog=generate_blog) 
    else:
        print("no blog generated")

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Blog is generated!')
    }
