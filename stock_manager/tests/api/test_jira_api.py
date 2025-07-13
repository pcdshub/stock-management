from jira import Issue, JIRA


def main():
	api_key = ('ATATT3xFfGF0PS7Wy_fT4qtSU3ZeF90NLUoOQe04vSB25esAMUtYZBWLVPLZG24GuPvESMDlEDz3xAyb7hoNY'
			   '-DpZWdt6TnrPRNvg3fm65hHHllE5UeqwhZi4Nfv6mbfpzu59GQYLBDhD-gSXI46Plz2PtoVbLCqKyybHTLekG6J1LmJPwOI0c0'
			   '=926A2351')
	_jira = JIRA(
			options={
				'server': 'https://slac-project-test.atlassian.net/'
			},
			basic_auth=('landen@slac.stanford.edu', api_key))
	
	# for project in _jira.projects():
	# 	print(project.key)
	
	# list_all_issues(_jira)
	
	issue = create_issue(_jira, 'summary here', 'description here', 'Feature')


# print(get_issue_attribute(issue, 'summary'))

# update_issue(issue, {'summary': 'some other summary here'})


def list_all_issues(client: JIRA):
	for issue in client.search_issues(f'project=KAN'):
		print(f"Key: {issue.key}, Summary: {issue.fields.summary}, Desc: {issue.fields.description}")


def create_issue(client: JIRA, summary: str, desc: str, type: str) -> Issue:
	return client.create_issue(
			{'project': {'key': 'KAN'}, 'summary': summary, 'description': desc, 'issuetype': {'name': type}})


def delete_issue(issue: Issue):
	issue.delete()


def get_issue_attribute(issue: Issue, attribute: str):
	return issue.get_field(attribute)


def update_issue(issue, update_dict):
	issue.update(update_dict)


if __name__ == '__main__':
	main()
