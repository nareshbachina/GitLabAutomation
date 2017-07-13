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
    
def main(connection,gitlab_repos,branch,version):
  for repo in gitlab_repos:
    print bcolors.BOLD+'******************************** '+repo+' *********************************************'+bcolors.ENDC
    try:
      project=connection.projects.get(repo)
      print bcolors.OKBLUE+'Found '+repo+' repository:  '+'SUCCESS'+bcolors.ENDC
      if check_branch(connection,repo,project.id,branch):
        print bcolors.OKBLUE+'Found '+branch+' branch for '+repo+': '+'SUCCESS'+bcolors.ENDC
        update_properties_file(connection,repo,project,branch,version=version)
      else:
        print bcolors.FAIL+'Found '+branch+' branch for '+repo+': '+'FAILED'+bcolors.ENDC
    except Exception as e:
      print bcolors.FAIL+'Found '+repo+' repository:  '+'FAILED'+bcolors.ENDC
      print bcolors.BOLD+'Cause of Failure:'+bcolors.ENDC
      print e
      continue
    print '\n'
if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option('--branch',help='provide the branch in which to update properties file.(Mandatory)',type='str',dest='branch')
  parser.add_option('--version',help='provide the version.',type='str',dest='version')
  (options,args) = parser.parse_args()
  
  if options.branch and options.branch!="None":
    branch=options.branch
  else:
    parser.print_help()
    exit()
  if options.version and options.version!="None":
    version=options.version
  else:
    version=None
 
config_file='config.yml'
config_data = read_config(config_file)
gitlab_url = config_data['gitlab_url']
gitlab_email = config_data['gitlab_email']
gitlab_password = config_data['gitlab_password']
gitlab_repos_file = config_data['gitlab_repos_file']
local_gitlab_repos=read_repos_config(gitlab_repos_file)
connection=auth_gitlab(gitlab_url,gitlab_email,gitlab_password)
print '\n'
main(connection,local_gitlab_repos,branch,version)
