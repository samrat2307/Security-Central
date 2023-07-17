-- Solutions
insert into solution(name) values('MSC');
insert into solution(name) values('SP');
insert into solution(name) values('CS');
insert into solution(name) values('MSE');
insert into solution(name) values('Studio');
insert into solution(name) values('ECOI');

-- Release
insert into release(name, release_date) values('2023.1', '2023-03-15'); 

-- Projects
insert into project(name, blackduck_project_name, solution_id) values('Client Adapter', 'ACT-FMC-MSC-CLIENTADAPTER', 1);
insert into project(name, blackduck_project_name, solution_id) values('Client Adapter', 'ACT-FMC-REDEYE', 1);
insert into project(name, blackduck_project_name, solution_id) values('SP Client Adapter', 'ACT-FMC-SP-CLIENTADAPTER', 2);
insert into project(name, blackduck_project_name, solution_id) values('Alert Distributor', 'ACT-FMC-ALERT-DISTRIBUTOR', 2);
	 
	
	
-- Scan
insert into scan(release_id,project_id,report_file) values(1,1,'components.csv');