import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

export class MyS3DynamoDBStack extends cdk.Stack {
  public readonly bucket: s3.Bucket;
  public readonly table: dynamodb.Table;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here
    // Create the S3 bucket
    this.bucket = new s3.Bucket(this, 'newS3Bucket', {
      bucketName: 'luxu-6620hw3-bucket',
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // Delete bucket on stack removal
    });

    // Create the DynamoDB table
    this.table = new dynamodb.Table(this, 'S3ObjectSizeHistoryTable', {
      tableName: 'S3-object-size-history',
      partitionKey: { name: 'bucket_name', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      removalPolicy: cdk.RemovalPolicy.DESTROY, // Delete table on stack removal
    });

    // Add Global Secondary Index (GSI)
    this.table.addGlobalSecondaryIndex({
      indexName: 'MaxSizeIndex',
      partitionKey: { name: 'bucket_name', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'size_bytes', type: dynamodb.AttributeType.NUMBER },
      projectionType: dynamodb.ProjectionType.KEYS_ONLY,
    });

    // Output the bucket name & table name in the terminal after deployment
    new cdk.CfnOutput(this, 'S3BucketName', { value: this.bucket.bucketName });
    new cdk.CfnOutput(this, 'DynamoDBTableName', { value: this.table.tableName });

  }
}
