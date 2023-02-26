
# Abiquo wiki scripts repository

This was my learning repository for many years.
Here are some examples of my projects.

## Starting with AWK
I started automating my docs with shell scripts that contained AWK commands that read code.
For example, the Java [AWK to process API Error file](https://github.com/mjsmyth/abiquo-wiki-scripts/blob/master/process_api_error/process_api_error_dev_guide.sh)

I also got the developers to commit to a central configuration properties file.
And then ran a script [AWK to process properties file](https://github.com/mjsmyth/abiquo-wiki-scripts/blob/master/properties/process_properties.sh)

## Python script for a customer use case
A common customer use case is to [create a tenant in the cloud platform](https://abiquo.atlassian.net/wiki/spaces/doc/pages/311378926/Abiquo+cloud+broker+tenant+creation+guide) 
The customer will then automate this action with the API.
I created a very quick Python script to [test the steps in the customer use case](https://github.com/mjsmyth/abiquo-wiki-scripts/blob/master/customer_script/abiquotenant.py)
I later also created a document to describe the steps: [how-to create a tenant via API](https://abiquo.atlassian.net/wiki/spaces/doc/pages/311375969/How+to+create+a+tenant+via+API).


## Python to implement API how-tos
I enjoyed using Python to implment [How to add a NAT rule via API](https://abiquo.atlassian.net/wiki/spaces/doc/pages/311375630/How+to+add+a+NAT+rule+to+a+VM+via+API) 
The Python script is very basic, because it is just to test the process.
See [Add a NAT rule to a VM with Python](https://github.com/mjsmyth/abiquo-wiki-scripts/blob/master/api_howtos/vm_add_nat_rules.py) 


## Check API docs for missing data
I had an HTML version of the API docs and I used Python to scan it for missing data.
See [Check roles or privileges in API docs](https://github.com/mjsmyth/abiquo-wiki-scripts/blob/master/checkroles/Checkroles.py)


## Migrating to Confluence Cloud
As part of the migration, I automated many tasks, such as [Check which editor the page is using](https://github.com/mjsmyth/abiquo-wiki-scripts/blob/master/confluence_cloud_migration/ccloGetEditor.py)


## Add data for screenshots using the product API
There were some new UI screens that displayed custom metrics that users can add with the API.
So to get some screenshots with data, I wrote a very rough script to [push custom metrics](https://github.com/mjsmyth/abiquo-wiki-scripts/blob/master/general/metrics_push.py)

