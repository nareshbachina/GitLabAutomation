#!/usr/bin/python
import gitlab
import yaml
import optparse
import base64

# Defined class for setting the colors for output.
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# Method to get all the files present in repo with the given file name.
def get_all_files(connection,project,branch,file_name):
  file_list=[]
  repository_tree=project.repository_tree(recursive=True,branch=branch)
  for item in repository_tree:
    if item['type']=='blob' and item['name']==file_name:
      file_list.append(str(item['path']))
  return file_list

# Method to read the repositories from the repositories.yml file.
def read_repos_config(file_name):
  with open(file_name) as f:
    try:
      projects = yaml.load(f)['repositories']
      print bcolors.OKBLUE+'Reading the projects from '+file_name+' file: '+'SUCCESS'+bcolors.ENDC
    except Exception as e:
      print bcolors.FAIL+'Reading the projects from '+file_name+' file: '+'FAILED'+bcolors.ENDC
      print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
      print e
      exit()
  return projects
  
# Method to create a branch for the given repository.
def create_branch(connection,repository_name,project_id,base_branch,new_branch):
  try:
    connection.project_branches.create({'branch_name': new_branch,'ref': base_branch},project_id=project_id)
    print bcolors.OKBLUE+'Creation of '+new_branch+' branch from '+base_branch+' branch for '+repository_name+' repository: '+'SUCCESS'+bcolors.ENDC
  except Exception as e:
    print bcolors.FAIL+'Creation of '+new_branch+' branch from '+base_branch+' branch for '+repository_name+' repository: '+'FAILED'+bcolors.ENDC
    print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
    print e
    
# Method to check if particular branch exists for the given repository.
def check_branch(connection,repository_name,project_id,branch):
  branches=connection.project_branches.list(project_id=project_id)
  found=False
  for each_branch in branches:
    if each_branch.name==branch:
      found=True
  return found

# Method to update the file in newly created branch with version=test as version=given version
def update_properties_file(connection,repository_name,project,branch,version):
  file_name='file_name.txt'
  files_list=get_all_files(connection,project,branch,file_name)
  for file in files_list:
    try:
      f=connection.project_files.get(file_path=file,ref=branch,project_id=project.id)
      #print bcolors.OKBLUE+'Found '+file+' in '+branch+' branch of '+repository_name+' repository: '+'SUCCESS'+bcolors.ENDC
      old_data=f.decode().split('\n')
      for i in range(len(old_data)):
        if old_data[i].startswith('version=') and version and version!="None":
          old_data[i]="version=\""+version+"-SNAPSHOT\""
      new_data='\n'.join(old_data)
      content=base64.b64encode(new_data)
      f.content=content
      try:
        f.save(branch_name=branch,commit_message='Updated the version in Gradle Properties file.')
        print bcolors.OKBLUE+'Updation of '+file+' in '+branch+' branch of '+repository_name+' repository: '+'SUCCESS'+bcolors.ENDC
      except Exception as e:
        print bcolors.FAIL+'Updation of '+file+' in '+branch+' branch of '+repository_name+' repository: '+'FAILED'+bcolors.ENDC
        print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
        print e
    except Exception as e:
      print bcolors.FAIL+'Found '+file+' in '+branch+' branch of '+repository_name+' repository: '+'FAILED'+bcolors.ENDC
      print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
      print e


# Method to make a branch as protected.
def protect_branch(connection,repository_name,project_id,branch,developers_can_push,developers_can_merge):
  to_protect_branch=connection.project_branches.get(project_id=project_id,id=branch)
  try:
    to_protect_branch.protect(developers_can_push=developers_can_push,developers_can_merge=developers_can_merge)

    print bcolors.OKBLUE+'Protection (developers can push='+str(developers_can_push)+' ,developers_can_merge='+str(developers_can_merge)+') of '+branch+' branch of '+repository_name+' repository: '+'SUCCESS'+bcolors.ENDC

  except Exception as e:

    print bcolors.FAIL+'Protection (developers can push='+str(developers_can_push)+' ,developers_can_merge='+str(developers_can_merge)+') of '+branch+' branch of '+repository_name+' repository: '+'FAILED'+bcolors.ENDC
    print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
    print e
    
# Method to create and merge a merge request.
def create_merge_request(connection,project_id,source_branch,target_branch,title,approve):
    try:
        mr=connection.project_mergerequests.create({'source_branch': source_branch,'target_branch': target_branch,'title': title},project_id=project_id)
        print bcolors.OKBLUE+'Creation of merge request for '+source_branch+' to '+target_branch+': SUCCESS'+bcolors.ENDC
    except Exception as e:
        print bcolors.FAIL+'Creation of merge request for '+source_branch+' to '+target_branch+': FAILED'+bcolors.ENDC
        print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
        print e
        return False
    if approve==True:
    	try:
          mr.merge()
          print bcolors.OKBLUE+'Merge request approval: SUCCESS'+bcolors.ENDC
        except Exception as e:
          print bcolors.FAIL+'Merge request approval: FAILED'+bcolors.ENDC
          print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
          print e
        
# Method for Authenticating to Gitlab.
def auth_gitlab(gitlab_url,email,password):
  gl=gitlab.Gitlab(gitlab_url,email=email,password=password)
  try:
    gl.auth()
    print bcolors.OKBLUE+'Authentication to '+gitlab_url+' with provided username and password: '+'SUCCESS'+bcolors.ENDC
  except Exception as e:
    print bcolors.OKBLUE+'Authentication to '+gitlab_url+' with provided username and password: '+'FAILED'+bcolors.ENDC
    print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
    print e
    exit()
  return gl

# Method to read the Config file where we store gitlab url,username,password,base branch,repos file.
def read_config(file_name):
  with open(file_name) as f:
    try:
      projects = yaml.load(f)
      print bcolors.OKBLUE+'Reading the config from '+file_name+' file: '+'SUCCESS'+bcolors.ENDC
    except Exception as e:
      print bcolors.FAIL+'Reading the config from '+file_name+' file: '+'FAILED'+bcolors.ENDC
      print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
      print e
      exit()
  return projects
