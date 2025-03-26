#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { MyS3DynamoDBStack } from '../lib/s3-dynamodb-stack';
import { MyLambdaStack } from '../lib/lambda-stack';

const app = new cdk.App();

// Deploy the S3 and DynamoDB stack
const storageStack = new MyS3DynamoDBStack(app, 'MyS3DynamoDBStack');

// Deploy the Lambda stack, passing the S3 bucket name and DynamoDB table name
new MyLambdaStack(app, 'MyLambdaStack', {
  bucketName: storageStack.bucket.bucketName,
  tableName: storageStack.table.tableName,
});

app.synth();
