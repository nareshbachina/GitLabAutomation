from methods import *
import optparse


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main(connection,gitlab_repos,target_branch,source_branch):
  for repo in gitlab_repos:
    print bcolors.BOLD+'******************************** '+repo+' *********************************************'+bcolors.ENDC
    try:
      project=connection.projects.get(repo)
      print bcolors.OKBLUE+'Found '+repo+' repository:  '+'SUCCESS'+bcolors.ENDC
      protect_branch(connection,repo,project.id,source_branch,False,False)
      if check_branch(connection,repo,project.id,source_branch):
        print bcolors.OKBLUE+'Found '+source_branch+' branch(from which it needs to create a new branch) for '+repo+': '+'SUCCESS'+bcolors.ENDC
        create_branch(connection,repo,project.id,source_branch,target_branch)
        protect_branch(connection,repo,project.id,source_branch,True,False)
      else:
        print bcolors.FAIL+'Found '+source_branch+' branch(from which it needs to create a new branch) for '+repo+': '+'FAILED'+bcolors.ENDC
    except Exception as e:
      print bcolors.FAIL+'Found '+repo+' repository:  '+'FAILED'+bcolors.ENDC
      print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
      print e
      continue
    print '\n'
    
if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('--target_branch',help='provide the name of branch to create(mandatory)',type='str',dest='target_branch')
  parser.add_option('--source_branch',help='provide the name of branch from which we need to create target branch(mandatory)',type='str',dest='source_branch')
    
  (options,args) = parser.parse_args()
  
  if options.target_branch and options.target_branch!="None":
    target_branch=options.target_branch
  else:
    parser.print_help()
    exit()
  if options.source_branch and options.source_branch!="None":
    source_branch=options.source_branch
  else:
    parser.print_help()
    exit()
 
  config_file='config.yml'
  config_data = read_config(config_file)
  gitlab_url = config_data['gitlab_url']
  gitlab_email = config_data['gitlab_email']
  gitlab_password = config_data['gitlab_password']
  gitlab_repos_file = config_data['gitlab_repos_file']
  local_gitlab_repos=read_repos_config(gitlab_repos_file)
  connection=auth_gitlab(gitlab_url,gitlab_email,gitlab_password)
  print '\n'
  main(connection,local_gitlab_repos,target_branch,source_branch)
