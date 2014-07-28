# mysql
> use kinton

SELECT p.name 'Privilege Name', r.name 'Role Name' FROM role r inner join roles_privileges rp on rp.idRole = r.idRole inner join privilege p on rp.idPrivilege = p.idPrivilege WHERE r.name = 'CLOUD_ADMIN' OR r.name = 'ENTERPRISE_ADMIN' OR r.name = 'USER' OR r.name = 'OUTBOUND_API_EVENTS';

