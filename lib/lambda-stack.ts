import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import * as path from 'path';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';

export interface MyLambdaProps extends cdk.StackProps {
  bucketName: string;
  tableName: string;
}

export class MyLambdaStack extends cdk.Stack {
  public readonly sizeTrackingLambda: lambda.Function;
  public readonly plottingLambda: lambda.Function;
  public readonly driverLambda: lambda.Function;

  constructor(scope: Construct, id: string, props: MyLambdaProps) {
    super(scope, id, props);
    const { bucketName, tableName } = props;

    // Matplotlib Layer ARN
    const matplotlibLayer = lambda.LayerVersion.fromLayerVersionArn(
      this,
      'MatplotlibLayer',
      'arn:aws:lambda:us-west-2:770693421928:layer:Klayers-p311-matplotlib:15', 
    );

    // Size Tracking Lambda
    this.sizeTrackingLambda = new lambda.Function(this, 'SizeTrackingLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'size_tracking_lambda_function.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda')),
      environment: {
        BUCKET_NAME: bucketName,
        DDB_TABLE_NAME: tableName,
      },
      timeout: cdk.Duration.seconds(30),
      memorySize: 512,
    });

    // Attach event notifications to S3 bucket
    const bucket = s3.Bucket.fromBucketAttributes(this, 'Bucket', {
      bucketArn: `arn:aws:s3:::${bucketName}`,
      bucketName: bucketName,
    });
    bucket.addEventNotification(s3.EventType.OBJECT_CREATED, new s3n.LambdaDestination(this.sizeTrackingLambda));
    bucket.addEventNotification(s3.EventType.OBJECT_REMOVED, new s3n.LambdaDestination(this.sizeTrackingLambda));

    // Grant permissions to size tracking Lambda
    this.sizeTrackingLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['s3:GetObject', 's3:ListBucket'],
      resources: [`${bucket.bucketArn}`, `${bucket.bucketArn}/*`],
    }));
    this.sizeTrackingLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['dynamodb:PutItem', 'dynamodb:UpdateItem'],
      resources: [`arn:aws:dynamodb:us-west-2:*:table/${tableName}`],
    }));

    // Plotting Lambda
    this.plottingLambda = new lambda.Function(this, 'PlottingLambda', {
      runtime: lambda.Runtime.PYTHON_3_11, // align with the layer version
      handler: 'plotting_lambda_function.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda')),
      environment: {
        BUCKET_NAME: bucketName,
        DDB_TABLE_NAME: tableName,
      },
      layers: [matplotlibLayer],
      timeout: cdk.Duration.seconds(30),
      memorySize: 1024,
    });

    // Grant Plotting Lambda read access to DynamoDB table and write access to S3 bucket
    this.plottingLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['dynamodb:Scan', 'dynamodb:Query'],
      resources: [`arn:aws:dynamodb:us-west-2:*:table/${tableName}`],
    }));
    this.plottingLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['s3:PutObject'],
      resources: [`${bucket.bucketArn}/*`],
    }));

    this.plottingLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['dynamodb:Query'],
      resources: [
        'arn:aws:dynamodb:us-west-2:021891594255:table/S3-object-size-history',
        'arn:aws:dynamodb:us-west-2:021891594255:table/S3-object-size-history/index/MaxSizeIndex'
      ],
    }));    

    // API Gateway for Plotting Lambda
    const api = new apigateway.LambdaRestApi(this, 'PlottingAPI', {
      handler: this.plottingLambda,
      proxy: false,
    });

    const plottingResource = api.root.addResource('plot');
    plottingResource.addMethod('GET'); // HTTP GET to trigger the lambda

    // Driver Lambda
    this.driverLambda = new lambda.Function(this, 'DriverLambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'driver_lambda_function.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda')),
      environment: {
        PLOTTING_API_URL: api.url + 'plot', // API endpoint for Plotting Lambda
        BUCKET_NAME: bucketName,
      },
      timeout: cdk.Duration.seconds(60), // Increase timeout to 60 seconds
      memorySize: 512,
    });

    // Grant Driver Lambda full S3 access
    this.driverLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['s3:*'],
      resources: [`${bucket.bucketArn}`, `${bucket.bucketArn}/*`],
    }));

    // Grant CloudWatch permissions to all Lambda functions
    const cloudWatchPolicy = new iam.PolicyStatement({
      actions: ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
      resources: ['arn:aws:logs:*:*:*'],
    });
    
    this.sizeTrackingLambda.addToRolePolicy(cloudWatchPolicy);
    this.plottingLambda.addToRolePolicy(cloudWatchPolicy);
    this.driverLambda.addToRolePolicy(cloudWatchPolicy);
    

    // Grant Driver Lambda API Gateway invoke permissions
    this.driverLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['execute-api:Invoke'],
      resources: [`${api.arnForExecuteApi()}`],
    }));
  }
}


