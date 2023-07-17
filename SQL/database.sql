create table solution
(
	id int generated always AS identity,
	name varchar(64) not null,
	last_updated timestamp default current_timestamp,
	primary key(id)
);


create table release
(
	id int generated always as identity,
	name varchar(64) not null,
	release_date date null,
	last_updated timestamp default current_timestamp,
	primary key(id)
);

create table project
(
	id int generated always as identity,
	name varchar(64) not null,
	blackduck_project_name varchar(64) not null,
	solution_id int not null, 
	auto_monitor boolean not null default FALSE,
	last_updated timestamp default current_timestamp,	
	constraint fk_solution foreign key(solution_id) references solution(id),
	primary key(id)
);

create table component
(
	id int generated always as identity,
	blackduck_component_id varchar(40) not null,
	blackduck_version_id varchar(40) not null,
	name varchar(50) not null,	
	version varchar(20) not null,
	last_updated timestamp default current_timestamp,
	primary key(id)	
);

create table scan
(
	id int generated always as identity,
	release_id int not null,
	project_id int not null,
	scan_datetime timestamp not null default current_timestamp,
	report_file varchar(256) not null,
	constraint fk_release foreign key(release_id) references release(id),
	constraint fk_project foreign key(project_id) references project(id),
	primary key(id)
);

create table scan_details
( 
	id bigint generated always as identity,
	scan_id int not null,
	component_id int not null,
	critical_vulnerability_count int not null default 0,
	high_vulnerability_count int not null default 0,
	medium_vulnerability_count int not null default 0,
	low_vulnerability_count int not null default 0,
	operational_risk varchar(10) null,
	license_name varchar(100) null,
	constraint fk_scan foreign key(scan_id) references scan(id),
	constraint fk_component foreign key(component_id) references component(id),
	primary key(id)
);

