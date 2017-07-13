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
def main(connection,gitlab_repos,source_branch,target_branch,title,approve):
  for repo in gitlab_repos:
    print bcolors.BOLD+'******************************** '+repo+' *********************************************'+bcolors.ENDC
    try:
      project=connection.projects.get(repo)
      print bcolors.OKBLUE+'Found '+repo+' repository:  '+'SUCCESS'+bcolors.ENDC
      if check_branch(connection,repo,project.id,source_branch):
        print bcolors.OKBLUE+'Found '+source_branch+' branch for '+repo+': '+'SUCCESS'+bcolors.ENDC
        create_merge_request(connection,project.id,source_branch,target_branch,title,approve)
      else:
        print bcolors.FAIL+'Found '+source_branch+' branch for '+repo+': '+'FAILED'+bcolors.ENDC
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
  parser.add_option('--title',help='provide the name of title for Merge Request(mandatory)',type='str',dest='title')
  parser.add_option('--approve',help='Whether to approve Merge Request or not(optional default is True) or provide False',type='str',dest='approve')
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
    
  if options.title and options.title!="None":
    title=options.title
  else:
    parser.print_help()
    exit()
  if options.approve and options.approve!="None":
    approve=options.approve
    if approve=="true" or approve==True:
      approve=True
    elif approve=="false" or approve==False:
      approve=False
    else:
      print "approve option takes only boolean values.(true or false)"
      exit()
  else:
    approve=True
    
  config_file='config.yml'
  config_data = read_config(config_file)
  gitlab_url = config_data['gitlab_url']
  gitlab_email = config_data['gitlab_email']
  gitlab_password = config_data['gitlab_password']
  gitlab_repos_file = config_data['gitlab_repos_file']
  local_gitlab_repos=read_repos_config(gitlab_repos_file)
  connection=auth_gitlab(gitlab_url,gitlab_email,gitlab_password)
  print '\n'
  main(connection,local_gitlab_repos,source_branch,target_branch,title,approve)
