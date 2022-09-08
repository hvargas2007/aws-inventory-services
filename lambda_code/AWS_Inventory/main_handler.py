from inventory import *
from store_data import *
import logging, os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
bucket_name = os.environ.get('bucket_name')
scan_local_account = True

def lambda_handler(event, context):
    logger.info(f'event: {event}')

    EC2_Inventory = []
    EC2_Inventory.clear()
    RDS_Inventory = []
    RDS_Inventory.clear()
    AWS_Inventory = []
    AWS_Inventory.clear()
    
    try:
        #Get Inventory Data:
        availability_zones = get_availability_zones()
        if scan_local_account == True:
            #EC2:
            get_ec2_local(EC2_Inventory, availability_zones)
            get_ec2_cross_accounts_router(EC2_Inventory, availability_zones)
            
            #RDS:
            get_rds_local(RDS_Inventory)
            get_rds_cross_accounts_router(RDS_Inventory)
        
        else:
            #EC2:
            get_ec2_cross_accounts_router(EC2_Inventory, availability_zones)
            #RDS:
            get_rds_cross_accounts_router(RDS_Inventory)
        
        #Store Inventory in S3:
        save_json(EC2_Inventory, RDS_Inventory)
        push_to_s3(bucket_name)
        
        for index in EC2_Inventory:
            AWS_Inventory.append(index)
        for index in RDS_Inventory:
            AWS_Inventory.append(index)
            
        return AWS_Inventory
    
    except Exception as error:
        logger.error(error)
        return {
            'statusCode': 400,
            'message': 'An error has occurred',
            'moreInfo': {
                'Lambda Request ID': '{}'.format(context.aws_request_id),
                'CloudWatch log stream name': '{}'.format(context.log_stream_name),
                'CloudWatch log group name': '{}'.format(context.log_group_name)
                }
            }