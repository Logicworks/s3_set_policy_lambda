# Set Policy Lambda Function

This is a python script that will set update the Policy statements for s3 buckets and secrets manager. It is called by 
an SNS topic in the master account when a new account is created.  The SNS topic passes in a json object that has the 
name of the policy, type (S3, Secrets, KMS Keys), and all the account numbers. It will use a JINJA2 template to create 
the policy Statment.

Uses
* [AWS SAM](https://aws.amazon.com/serverless/sam/) to build, package and deploy the lambda function.
* [Jinja2](http://jinja.pocoo.org/) to build the policy statments.

## Diagram on how it works.

<object data="https://github.com/Chewy-Inc/set_policies_lambda/blob/master/SetPolicyStatemets.pdf" type="application/pdf" width="700px" height="700px">
    <embed src="https://github.com/Chewy-Inc/set_policies_lambda/blob/master/SetPolicyStatemets.pdf" type="application/pdf"  >
        <p>This browser does not support PDFs. Please download the PDF to view it: <a href="https://github.com/Chewy-Inc/set_policies_lambda/blob/master/SetPolicyStatemets.pdf">Download PDF</a>.</p>
    </embed>
</object>

<embed src="SetPolicyStatemets.pdf" type="application/pdf"   height="700px" width="500">


## SNS Topic

* Elements
  * policyNames
    * type: The type of policies. Vaild types are s3, secrets, kms
    * name: The name of the policy it must match the name of the jinja2 template file in the templates directory. 
    * keyarn: This is the KMS Key arn to have the policy updated.
  * accountids
    * The list of account ids you want to have allowed access to these policy statements.


```json
{
   "policyNames": [ 
       { "type"    : "kms",
         "name"    :"secretsmanager",
         "keyarn"  : "arn:aws:kms:us-east-1:111111111111:key/1a5fda48-6bda-4a56-9c60-22ccb0fb8348"
       },
       { "type" : "s3",
         "name" : "ss-cf-templates" 
       },
       { "type" : "s3",
         "name" :"ss-cf-templates"
       
       },
       { "type" : "s3",
         "name" :"ss-terraform-state"
       
       },
       { "type" : "secrets",
         "name" :"artifactory-docker-user"
       
       }
   ],
   "accountids": [
       "111111111111",
       "222222222222",
       "333333333333",
       "444444444444",
       "555555555555",
       "666666666666",
       "777777777777",
       "888888888888",
       "999999999999"
   ]
}
```





